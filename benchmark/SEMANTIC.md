# Semantic evaluation — did the rules change behavior without losing signal?

Per cell: % of runs exhibiting each marker (lower is better for unwanted traits), and judge correctness. Evaluated on captured responses; N=5 runs/cell.

Marker legend: pre=preamble, syc=sycophancy, close=closing fluff, ai='as an AI', em=em-dash, sq=smart-quotes. acc/comp/key = judge accurate/complete/key-point.


## haiku

| Test | Cond | pre | syc | close | ai | em | sq | acc | comp | key |
|---|---|---|---|---|---|---|---|---|---|---|
| T1-async | baseline | 0% | 0% | 0% | 0% | 80% | 0% | 100% | 100% | 100% |
|  | CLAUDE.md | 0% | 0% | 0% | 0% | 100% | 0% | 100% | 100% | 100% |
| T2-review | baseline | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 100% | 100% |
|  | CLAUDE.md | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 100% | 100% |
| T3-rest | baseline | 0% | 0% | 0% | 0% | 80% | 0% | 100% | 100% | 100% |
|  | CLAUDE.md | 0% | 0% | 0% | 0% | 100% | 0% | 100% | 100% | 100% |
| T4-prompt | baseline | 0% | 0% | 20% | 0% | 100% | 0% | 100% | 100% | 0% |
|  | CLAUDE.md | 0% | 0% | 0% | 0% | 100% | 0% | 100% | 100% | 0% |
| T5-halluc | baseline | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 100% | 100% |
|  | CLAUDE.md | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 100% | 100% |

## opus

| Test | Cond | pre | syc | close | ai | em | sq | acc | comp | key |
|---|---|---|---|---|---|---|---|---|---|---|
| T1-async | baseline | 0% | 0% | 0% | 0% | 100% | 0% | 100% | 100% | 100% |
|  | CLAUDE.md | 0% | 0% | 0% | 0% | 100% | 0% | 100% | 100% | 100% |
| T2-review | baseline | 0% | 0% | 0% | 0% | 80% | 0% | 100% | 100% | 100% |
|  | CLAUDE.md | 0% | 0% | 0% | 0% | 100% | 0% | 100% | 100% | 100% |
| T3-rest | baseline | 0% | 0% | 0% | 0% | 100% | 0% | 100% | 100% | 100% |
|  | CLAUDE.md | 0% | 0% | 0% | 0% | 100% | 0% | 100% | 100% | 100% |
| T4-prompt | baseline | 0% | 0% | 0% | 0% | 100% | 0% | 100% | 100% | 0% |
|  | CLAUDE.md | 0% | 0% | 0% | 0% | 100% | 0% | 100% | 80% | 0% |
| T5-halluc | baseline | 0% | 0% | 0% | 0% | 80% | 0% | 100% | 100% | 100% |
|  | CLAUDE.md | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 100% | 100% |

## sonnet

| Test | Cond | pre | syc | close | ai | em | sq | acc | comp | key |
|---|---|---|---|---|---|---|---|---|---|---|
| T1-async | baseline | 0% | 0% | 0% | 0% | 100% | 0% | 100% | 100% | 100% |
|  | CLAUDE.md | 0% | 0% | 0% | 0% | 100% | 0% | 100% | 100% | 100% |
| T2-review | baseline | 0% | 0% | 0% | 0% | 60% | 0% | 100% | 100% | 100% |
|  | CLAUDE.md | 0% | 0% | 0% | 0% | 60% | 0% | 100% | 100% | 100% |
| T3-rest | baseline | 0% | 0% | 0% | 0% | 100% | 0% | 100% | 100% | 100% |
|  | CLAUDE.md | 0% | 0% | 0% | 0% | 100% | 0% | 100% | 100% | 100% |
| T4-prompt | baseline | 0% | 0% | 80% | 0% | 100% | 0% | 100% | 100% | 0% |
|  | CLAUDE.md | 0% | 0% | 60% | 0% | 100% | 0% | 100% | 100% | 0% |
| T5-halluc | baseline | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 100% | 100% |
|  | CLAUDE.md | 0% | 0% | 0% | 0% | 0% | 0% | 100% | 100% | 100% |

## Reading it

- The file's stated targets are: concise, **no sycophantic openers**, **no closing fluff**. It does NOT contain rules about em-dash, 'as an AI', or multi-version format — so changes there (or lack of) are incidental.
- A real win = unwanted-marker % drops baseline→CLAUDE.md while **key-point stays ~100%** (correction/bug/explanation preserved = zero signal loss).

## Verdict

The benchmark's five "PASS" results assert behavioral fixes that, measured on
current models, are mostly fixes to behaviors the baseline no longer exhibits:

1. **Preamble, sycophancy, "as an AI", smart-quotes: 0% in the baseline itself**,
   every model. There is nothing for the file to remove — the un-instructed model
   already opens with the answer (e.g. baseline T2 starts "**Bug: off-by-one
   error.**"). T1/T2/T3/T5's behavioral claims test against ghosts.
2. **Em-dash (T3): not fixed.** The file has no typography rule, so em-dashes
   persist at 60–100% in both conditions.
3. **Multi-version format (T4): not delivered.** key_point_hit = 0% in *both*
   conditions — neither baseline nor CLAUDE.md returns the "3 versions" the
   benchmark credits to the optimized output.
4. **Correctness is identical (100% accurate/complete) with and without the file.**
   Good news — the file does no harm — but it also adds no signal the baseline
   lacked.
5. **The only non-noise behavioral effect** is mild closing-fluff reduction on the
   single prompt-generation task (T4: haiku 20→0%, sonnet 80→60%).

Net: the file neither degrades nor meaningfully improves output behavior on these
prompts. The headline "all 5 PASS / zero signal loss" is true only because the
tests are graded against a baseline that already passes.