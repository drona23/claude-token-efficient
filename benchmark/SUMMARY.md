# CLAUDE.md automated benchmark — three-model results

Harness: `benchmark/run.py`. Engine: `claude -p --output-format json` over OAuth,
each prompt in a fresh `/tmp` dir (baseline = empty dir, treatment = repo `CLAUDE.md`
copied in), `--setting-sources project` to block global settings/hooks.
N=5 runs per cell. Metric: mean output tokens per prompt (word count in parens).

Raw per-run data: `benchmark/raw-{haiku,sonnet,opus}.jsonl` (full response text,
token + cache + cost + duration per run). Per-model tables: `benchmark/report-*.md`.

## Total output tokens, baseline → CLAUDE.md

| Model  | All 5 prompts | T1–T3,T5 only (excl. T4 format test) | Cost (base → file) |
|--------|---------------|--------------------------------------|--------------------|
| haiku  | 2244 → 2227 **-1%**  | 1736 → 1718 **-1%**  | $0.0849 → $0.0865 |
| sonnet | 1659 → 1473 **-11%** | 1170 → 1114 **-5%**  | $0.2366 → $0.2363 |
| opus   | 2851 → 2753 **-3%**  | 2213 → 1877 **-15%** | $0.2731 → $0.2797 |

T4 ("Generate a prompt…") is a format test, not a length test — the rules push it
toward structured/multi-version output, which *adds* tokens (opus +38%, haiku/sonnet
mixed). Excluding it is the fairer length comparison and is what BENCHMARK.md's own
63% average does (it averages T1–T3, T5).

## Findings (directional — single-session means, output varies run-to-run)

1. **The published 63% reduction does not reproduce as a token reduction.**
   Real effect ranges from ~-1% (haiku) to -15% (opus, excl. T4). Nowhere near 63%.

2. **Effect scales with the model's default verbosity.** Opus, the chattiest
   baseline, has the most to trim (-15% excl. T4); haiku barely moves (-1%).

3. **Words drop more consistently than tokens.** Every model's word counts fall
   (e.g. opus T1 401→320w), but markdown/structure tokens partly offset the saving —
   so a word-count benchmark overstates the token (= cost) win.

4. **On these short prompts it's ~cost-neutral.** The file's per-turn input overhead
   roughly cancels the output saving (haiku/opus slightly up, sonnet flat). The README's
   own caveat holds: net savings need high output volume to offset the persistent input cost.

## Caveats

- N=5, single session, no statistical controls — directional signal only.
- Measures one-shot Q&A prompts, not the agentic/coding loops where the file is
  pitched to help most (see the repo's "Issue #1" cost-to-green benchmark for that).
- Reproduce: `python3 benchmark/run.py -n 5 --model {haiku,sonnet,opus}`.
- This file covers **tokens**. For whether the rules change *behavior* and preserve
  correctness (the core of each test), see `SEMANTIC.md`.
