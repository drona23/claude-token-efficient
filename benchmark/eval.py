#!/usr/bin/env python3
"""
Semantic evaluation of captured benchmark responses.

The token benchmark (run.py) measured length. This evaluates the CORE of each
BENCHMARK.md test: did the CLAUDE.md rules actually change the targeted behavior
(preamble, sycophancy, closing fluff, etc.) AND preserve correctness ("zero signal
loss")? Operates on already-captured result_text in benchmark/raw-*.jsonl, so it
re-runs NO prompts — only LLM-judge calls for content correctness.

Two layers per response:
  - mechanical detectors  : deterministic regex for typography/phrasing markers
  - LLM judge (haiku)     : accuracy + completeness + each test's key semantic point

Usage:
  python3 benchmark/eval.py                       # all raw-*.jsonl
  python3 benchmark/eval.py --raw benchmark/raw-opus.jsonl
  python3 benchmark/eval.py --no-judge            # mechanical markers only (free)
"""
import argparse
import glob
import json
import re
import shutil
import statistics
import subprocess
import tempfile
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Each test's targeted-behavior claim (from BENCHMARK.md) and the semantic point
# a correct answer must hit (graded by the judge).
TESTS = {
    "T1-async":  {"claim": "no preamble / no hollow closing / no 'as an AI'",
                  "key": "explains async/await: lets you write asynchronous (promise-based) code that reads synchronously; await pauses for a promise"},
    "T2-review": {"claim": "bug identified; no sycophantic opener; no unsolicited alternatives",
                  "key": "identifies the off-by-one bug: i<=arr.length should be i<arr.length, else it reads arr[arr.length] (undefined/out of bounds)"},
    "T3-rest":   {"claim": "no em dash; no 'as an AI'; no hollow closing",
                  "key": "correctly describes REST as an HTTP-based architectural style for APIs (resources, verbs, statelessness)"},
    "T4-prompt": {"claim": "returns multiple distinct versions; consistent format",
                  "key": "provides at least two distinct prompt versions for a meditation app"},
    "T5-halluc": {"claim": "correction made; no sycophantic opener",
                  "key": "corrects the false claim: Python was created by Guido van Rossum (Gosling created Java)"},
}

EM_DASH = re.compile(r"[—–]|(?<!\w)--(?!\w)")
SMART_Q = re.compile(r"[‘’“”]")
AS_AN_AI = re.compile(r"\bas an ai\b|\bas a language model\b|\bi am just an ai\b", re.I)
PREAMBLE = re.compile(
    r"^\W*(sure|great|absolutely|certainly|of course|happy to|i'?d be happy|"
    r"i'?d love|good question|great question|excellent question|let me (help|take))",
    re.I)
SYCOPHANCY = re.compile(
    r"you'?re absolutely right|you are absolutely right|great question|great catch|"
    r"good question|excellent (question|point)|you'?re right|that'?s a (great|good)", re.I)
CLOSING = re.compile(
    r"hope (this|that) helps|let me know if|feel free to|happy to help|"
    r"anything else|don'?t hesitate|good luck|hope this (was )?help", re.I)


def markers(text: str) -> dict:
    """Deterministic behavior markers. True = the (usually unwanted) trait is present."""
    tail = text[-220:]
    # crude version count for T4: numbered/headed blocks
    versions = len(re.findall(r"(?im)^\s*(version|prompt|option)\s*\d|^\s*\d[\.\)]\s+\*?\*?(simple|detailed|creative|version)", text))
    return {
        "preamble": bool(PREAMBLE.search(text.strip())),
        "sycophancy": bool(SYCOPHANCY.search(text)),
        "closing_fluff": bool(CLOSING.search(tail)),
        "as_an_ai": bool(AS_AN_AI.search(text)),
        "em_dash": bool(EM_DASH.search(text)),
        "smart_quotes": bool(SMART_Q.search(text)),
        "version_count": versions,
    }


JUDGE_LOCK = threading.Lock()


def _judge_once(q: str) -> dict:
    with tempfile.TemporaryDirectory(prefix="cmd_eval_") as d:
        cmd = ["claude", "-p", q, "--model", "haiku",
               "--output-format", "json", "--setting-sources", "project"]
        proc = subprocess.run(cmd, cwd=d, capture_output=True, text=True)
    if proc.returncode != 0:
        return {"judge_error": (proc.stderr or proc.stdout).strip()[:120]}
    try:
        result = json.loads(proc.stdout).get("result", "")
        m = re.search(r"\{.*\}", result, re.S)
        return json.loads(m.group(0)) if m else {"judge_error": "no json"}
    except (json.JSONDecodeError, AttributeError):
        return {"judge_error": "parse"}


def judge(prompt: str, answer: str, key: str, retries: int = 4) -> dict:
    """Neutral haiku judge (no CLAUDE.md) grading content only — ignores tone/length.
    Retries with backoff so rate-limits / transient parse failures don't leave gaps."""
    q = (f"Grade an assistant answer for CONTENT ONLY (ignore tone, verbosity, formatting).\n"
         f"Question asked: {prompt}\n\n"
         f"Answer to grade:\n{answer}\n\n"
         f"Return ONLY compact JSON, no prose: "
         f'{{"accurate": bool, "complete": bool, "key_point_hit": bool, "reason": "<=8 words"}}\n'
         f"key_point_hit is true iff the answer: {key}")
    last = None
    for attempt in range(retries + 1):
        r = _judge_once(q)
        if "judge_error" not in r:
            if attempt:
                r["attempts"] = attempt + 1
            return r
        last = r
        if attempt < retries:
            err = r["judge_error"].lower()
            hot = any(s in err for s in ("rate", "429", "overload", "limit"))
            time.sleep((8 if hot else 3) * (attempt + 1))
    return last


def pct(vals):
    return f"{100*statistics.mean(vals):.0f}%" if vals else "-"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", action="append", default=[],
                    help="raw JSONL file(s); default = all benchmark/raw-*.jsonl")
    ap.add_argument("--no-judge", action="store_true", help="mechanical markers only")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--out", default=str(REPO / "benchmark" / "SEMANTIC.md"))
    args = ap.parse_args()

    files = args.raw or sorted(glob.glob(str(REPO / "benchmark" / "raw-*.jsonl")))
    records = []
    for f in files:
        for line in Path(f).read_text().splitlines():
            if line.strip():
                records.append(json.loads(line))
    records = [r for r in records if "error" not in r and r.get("result_text") is not None]
    print(f"loaded {len(records)} responses from {len(files)} file(s)")

    # mechanical markers (free)
    for r in records:
        r["markers"] = markers(r["result_text"])

    # llm judge (content) — parallel, on captured text only
    if not args.no_judge:
        def do(r):
            j = judge(r["prompt"], r["result_text"], TESTS[r["prompt_id"]]["key"])
            with JUDGE_LOCK:
                print(f"  judged {r['model']}/{r['condition']}/{r['prompt_id']}: "
                      f"{j.get('judge_error') or ('key' if j.get('key_point_hit') else 'MISS')}")
            return r, j
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for r, j in pool.map(do, records):
                r["judge"] = j

    report = render(records, judged=not args.no_judge)
    print("\n" + report)
    Path(args.out).write_text(report)
    print(f"\nwrote {args.out}")


def render(records, judged):
    # group by (model, prompt_id, condition)
    g = defaultdict(list)
    for r in records:
        g[(r["model"], r["prompt_id"], r["condition"])].append(r)
    models = sorted({r["model"] for r in records})
    conds = ["baseline", "CLAUDE.md"]

    out = ["# Semantic evaluation — did the rules change behavior without losing signal?\n",
           "Per cell: % of runs exhibiting each marker (lower is better for unwanted traits), "
           "and judge correctness. Evaluated on captured responses; N=5 runs/cell.\n",
           "Marker legend: pre=preamble, syc=sycophancy, close=closing fluff, "
           "ai='as an AI', em=em-dash, sq=smart-quotes. acc/comp/key = judge accurate/complete/key-point.\n"]

    for model in models:
        out.append(f"\n## {model}\n")
        out.append("| Test | Cond | pre | syc | close | ai | em | sq | "
                   + ("acc | comp | key |" if judged else ""))
        out.append("|---|---|---|---|---|---|---|---|" + ("---|---|---|" if judged else ""))
        for pid in TESTS:
            for cond in conds:
                rs = g.get((model, pid, cond), [])
                if not rs:
                    continue
                mk = [r["markers"] for r in rs]
                row = [pid if cond == "baseline" else "", cond,
                       pct([m["preamble"] for m in mk]),
                       pct([m["sycophancy"] for m in mk]),
                       pct([m["closing_fluff"] for m in mk]),
                       pct([m["as_an_ai"] for m in mk]),
                       pct([m["em_dash"] for m in mk]),
                       pct([m["smart_quotes"] for m in mk])]
                if judged:
                    js = [r.get("judge", {}) for r in rs]
                    js = [j for j in js if "judge_error" not in j]
                    row += [pct([j.get("accurate", False) for j in js]),
                            pct([j.get("complete", False) for j in js]),
                            pct([j.get("key_point_hit", False) for j in js])]
                out.append("| " + " | ".join(row) + " |")

    out.append("\n## Reading it\n")
    out.append("- The file's stated targets are: concise, **no sycophantic openers**, "
               "**no closing fluff**. It does NOT contain rules about em-dash, 'as an AI', "
               "or multi-version format — so changes there (or lack of) are incidental.")
    out.append("- A real win = unwanted-marker % drops baseline→CLAUDE.md while "
               "**key-point stays ~100%** (correction/bug/explanation preserved = zero signal loss).")
    return "\n".join(out)


if __name__ == "__main__":
    main()
