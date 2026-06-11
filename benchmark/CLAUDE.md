# Benchmark harness — operating instructions

Reproducible measurement of what `CLAUDE.md` does to model output: token cost
(`run.py`) and behavior/correctness (`eval.py`). Runs against the local `claude`
CLI over the existing login — no API key. Stdlib `python3` only.

## Method
Each prompt runs in a fresh temp dir so `CLAUDE.md` is the only variable:
baseline = empty dir; treatment = a `CLAUDE.md` copied in. `--setting-sources
project` blocks global settings/hooks. Metrics come from `claude -p
--output-format json` (real `output_tokens`, cost). Directional, not controlled —
use `-n 5`+ and read means as signal.

## Run the token benchmark
```bash
python3 run.py -n 5 --model haiku        # also: sonnet, opus
python3 run.py -n 5 --model sonnet --variant lean=../profiles/M-drona23-v8/CLAUDE.md
```
Flags: `-n` runs/cell, `--model haiku|sonnet|opus`, `--variant name=path`
(repeatable, vs baseline), `--workers` (**sweet spot 3**; 4+ trips rate limits and
thrashes on backoff; use 2 for opus). Retries with backoff; unrecoverable runs
logged as `error`+`attempts`.
Writes `report-<model>.md` (means, %) and `raw-<model>.jsonl` (per-run: text,
tokens, cost, duration).

## Run the semantic eval
Measures the *core* of each test (did behavior change; did correctness survive),
not length. Reads captured `result_text` — re-runs no prompts, only judge calls.
```bash
python3 eval.py --no-judge      # mechanical markers only, free, instant
python3 eval.py --workers 3     # + neutral haiku judge for correctness (3 = sweet spot)
```
Mechanical detectors: preamble, sycophancy, closing fluff, "as an AI", em-dash,
smart-quotes, T4 version count. Judge (haiku, no CLAUDE.md): `accurate`,
`complete`, `key_point_hit` per test. Writes `SEMANTIC.md`.

## Re-derive anything from raw data (no token spend)
`raw-*.jsonl` is the source of truth.
```bash
# mean output tokens by condition
jq -s 'group_by(.condition) | map({cond:.[0].condition, mean_out:(map(.output_tokens)|add/length)})' raw-sonnet.jsonl
# read the text behind a cell
jq -r 'select(.prompt_id=="T2-review" and .condition=="baseline") | .result_text' raw-opus.jsonl
# failures/retries
jq -c 'select(.error or .attempts) | {model,condition,prompt_id,run,error,attempts}' raw-*.jsonl
```
Fields: `model, condition, claude_md, prompt_id, prompt, run, ts, output_tokens,
words, cost, input_tokens, cache_*_input_tokens, num_turns, duration_ms,
session_id, result_text` (or `error`+`attempts`).

## Results
`SUMMARY.md` (tokens) and `SEMANTIC.md` (behavior). Full reproduction:
```bash
for m in haiku sonnet opus; do w=3; [ "$m" = opus ] && w=2; python3 run.py -n 5 --model "$m" --workers "$w"; done
python3 eval.py --workers 3
```
