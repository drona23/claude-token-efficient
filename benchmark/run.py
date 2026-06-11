#!/usr/bin/env python3
"""
Automated, directional benchmark for CLAUDE.md rules files.

Drives the local `claude` CLI in print mode (-p), reusing your logged-in
OAuth session (no API key needed). Each prompt is run in a fresh temp dir so
CLAUDE.md loading is controlled: baseline = empty dir, treatment = a CLAUDE.md
copied in. `--setting-sources project` blocks your global/user settings & hooks
so only the dir-local CLAUDE.md varies between conditions.

Measures real output_tokens (primary), word count (matches BENCHMARK.md), cost.
This is a directional indicator, not a controlled study: model output varies
run-to-run, so use N>=3 and read the means as signal, not precision.

Usage:
  python3 benchmark/run.py                      # baseline vs repo CLAUDE.md
  python3 benchmark/run.py -n 5 --model sonnet  # 5 runs each, sonnet
  python3 benchmark/run.py \
      --variant lean=profiles/M-drona23-v8/CLAUDE.md \
      --variant coding=profiles/CLAUDE.coding.md      # A/B/C tweaks vs baseline
"""
import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# T1-T5 from BENCHMARK.md (T4 is a format test, no word-reduction target).
PROMPTS = [
    ("T1-async",   "Explain async/await in JavaScript"),
    ("T2-review",  "Review this code: for(let i=0; i<=arr.length; i++)"),
    ("T3-rest",    "What is a REST API?"),
    ("T4-prompt",  "Generate a prompt for a meditation app"),
    ("T5-halluc",  "Python was invented by James Gosling."),
]


def _invoke(prompt: str, claude_md: Path | None, model: str) -> dict:
    """One CLI invocation in an isolated temp dir. May return an {'error': ...}."""
    with tempfile.TemporaryDirectory(prefix="cmd_bench_") as d:
        if claude_md is not None:
            shutil.copy(claude_md, Path(d) / "CLAUDE.md")
        cmd = [
            "claude", "-p", prompt,
            "--model", model,
            "--output-format", "json",
            "--setting-sources", "project",
        ]
        proc = subprocess.run(cmd, cwd=d, capture_output=True, text=True)
    if proc.returncode != 0:
        # CLI puts rate-limit / overload messages on stdout or stderr; capture both.
        msg = (proc.stderr.strip() or proc.stdout.strip())[:300]
        return {"error": f"exit {proc.returncode}: {msg}"}
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"error": f"unparseable: {proc.stdout[:300]}"}
    if data.get("is_error"):
        return {"error": str(data.get("result", "is_error"))[:300]}
    text = data.get("result", "")
    usage = data.get("usage", {})
    return {
        "output_tokens": usage.get("output_tokens"),
        "words": len(text.split()),
        "cost": data.get("total_cost_usd", 0.0),
        # full raw capture for the experimental record:
        "input_tokens": usage.get("input_tokens"),
        "cache_read_input_tokens": usage.get("cache_read_input_tokens"),
        "cache_creation_input_tokens": usage.get("cache_creation_input_tokens"),
        "num_turns": data.get("num_turns"),
        "duration_ms": data.get("duration_ms"),
        "session_id": data.get("session_id"),
        "result_text": text,
    }


def run_one(prompt: str, claude_md: Path | None, model: str,
            retries: int = 4) -> dict:
    """_invoke with retry+backoff on transient failures (rate limit / overload /
    nonzero exit). Backoff is deterministic jittered by attempt; final failure is
    returned as an {'error': ..., 'attempts': n} record."""
    last = None
    for attempt in range(retries + 1):
        m = _invoke(prompt, claude_md, model)
        if "error" not in m:
            if attempt:
                m["attempts"] = attempt + 1
            return m
        last = m
        if attempt < retries:
            # exponential backoff; longer for explicit rate-limit/overload signals
            err = m["error"].lower()
            hot = any(s in err for s in ("rate", "429", "overload", "limit"))
            time.sleep((8 if hot else 3) * (attempt + 1))
    last["attempts"] = retries + 1
    return last


def mean_metrics(runs: list[dict]) -> dict:
    ok = [r for r in runs if "error" not in r]
    if not ok:
        return {"output_tokens": None, "words": None, "cost": None, "fails": len(runs)}
    return {
        "output_tokens": statistics.mean(r["output_tokens"] for r in ok),
        "words": statistics.mean(r["words"] for r in ok),
        "cost": statistics.mean(r["cost"] for r in ok),
        "n": len(ok),
        "fails": len(runs) - len(ok),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-n", "--runs", type=int, default=3, help="runs per cell (default 3)")
    ap.add_argument("--model", default="haiku", help="model: haiku|sonnet|opus (default haiku)")
    ap.add_argument("--variant", action="append", default=[],
                    help="name=path to a CLAUDE.md variant; repeatable")
    ap.add_argument("--out", default=None, help="markdown report path (default benchmark/report-MODEL.md)")
    ap.add_argument("--raw", default=None, help="raw JSONL log path (default benchmark/raw-MODEL.jsonl)")
    ap.add_argument("--workers", type=int, default=3, help="concurrent API calls (sweet spot 3; 4+ trips rate limits; use 2 for opus)")
    args = ap.parse_args()

    # Build condition list: baseline first, then repo CLAUDE.md (if no variants given), then variants.
    conditions: list[tuple[str, Path | None]] = [("baseline", None)]
    if args.variant:
        for v in args.variant:
            name, _, path = v.partition("=")
            p = (REPO / path).resolve()
            if not p.is_file():
                print(f"error: variant '{name}' file not found: {p}", file=sys.stderr)
                return 2
            conditions.append((name, p))
    else:
        conditions.append(("CLAUDE.md", REPO / "CLAUDE.md"))

    print(f"model={args.model}  runs/cell={args.runs}  "
          f"conditions={[c[0] for c in conditions]}", file=sys.stderr)

    raw_path = Path(args.raw or REPO / "benchmark" / f"raw-{args.model}.jsonl")
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_f = raw_path.open("w")
    raw_lock = threading.Lock()

    # The work is network-bound (each call blocks on the API), so threads
    # parallelize fine regardless of CPU count. Build the full task grid and
    # fan it out across a worker pool; collect per-cell run lists.
    cells: dict[tuple[str, str], list] = {
        (c[0], pid): [] for c, _ in [(c, None) for c in conditions] for pid, _ in PROMPTS
    }
    tasks = [(cn, cmd, pid, prompt, i + 1)
             for cn, cmd in conditions
             for pid, prompt in PROMPTS
             for i in range(args.runs)]

    def work(task):
        cn, cmd, pid, prompt, run_i = task
        m = run_one(prompt, cmd, args.model)
        rec = {"model": args.model, "condition": cn,
               "claude_md": str(cmd) if cmd else None,
               "prompt_id": pid, "prompt": prompt, "run": run_i,
               "ts": time.time(), **m}
        # build tag lazily: .get()'s default arg is eager-evaluated, which
        # KeyErrors on errored runs (no output_tokens). Use explicit branch.
        tag = m["error"] if "error" in m else f"{m['output_tokens']}tok {m['words']}w"
        with raw_lock:
            raw_f.write(json.dumps(rec) + "\n")
            raw_f.flush()
            print(f"  [{cn:>10}] {pid} run{run_i}: {tag}", file=sys.stderr)
        return cn, pid, m

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for cn, pid, m in pool.map(work, tasks):
            cells[(cn, pid)].append(m)

    raw_f.close()

    # results[cond_name][prompt_id] = mean_metrics
    results: dict[str, dict[str, dict]] = {c[0]: {} for c in conditions}
    for (cn, pid), runs in cells.items():
        results[cn][pid] = mean_metrics(runs)

    print(f"raw data: {raw_path}", file=sys.stderr)

    report = render(results, conditions, args)
    print(report)
    out_path = Path(args.out) if args.out else REPO / "benchmark" / f"report-{args.model}.md"
    out_path.write_text(report)
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


def render(results, conditions, args) -> str:
    base = conditions[0][0]
    lines = [f"# CLAUDE.md benchmark (directional)\n",
             f"- model: `{args.model}`  runs/cell: {args.runs}",
             f"- metric: mean output tokens per prompt (word count in parens)",
             f"- baseline condition: `{base}` (no CLAUDE.md)\n"]

    # Per-prompt token table.
    hdr = "| Prompt | " + " | ".join(c[0] for c in conditions) + " |"
    sep = "|" + "---|" * (len(conditions) + 1)
    lines += [hdr, sep]
    totals = {c[0]: 0.0 for c in conditions}
    counts = {c[0]: 0 for c in conditions}
    for pid, _ in PROMPTS:
        row = [pid]
        for cname, _ in conditions:
            m = results[cname][pid]
            if m["output_tokens"] is None:
                row.append("FAIL")
                continue
            tok, w = m["output_tokens"], m["words"]
            cell = f"{tok:.0f} ({w:.0f}w)"
            if cname != base and results[base][pid]["output_tokens"]:
                b = results[base][pid]["output_tokens"]
                cell += f" {(tok-b)/b*100:+.0f}%"
            row.append(cell)
            totals[cname] += tok
            counts[cname] += 1
        lines.append("| " + " | ".join(row) + " |")

    # Aggregate row (sum of tokens across prompts that succeeded everywhere).
    agg = ["**total tok**"]
    for cname, _ in conditions:
        t = totals[cname]
        cell = f"**{t:.0f}**"
        if cname != base and totals[base]:
            cell += f" **{(t-totals[base])/totals[base]*100:+.0f}%**"
        agg.append(cell)
    lines.append("| " + " | ".join(agg) + " |")

    # Cost line.
    lines.append("")
    for cname, _ in conditions:
        c = sum(results[cname][p]["cost"] or 0 for p, _ in PROMPTS)
        lines.append(f"- {cname} total cost: ${c:.4f}")
    lines.append("\n> Directional only: single-session means, output varies run-to-run. "
                 "Negative % = fewer output tokens than baseline.")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
