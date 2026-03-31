# CLAUDE.md Universal - Validation Benchmark
# Project: PromptOS
# Date: 2026-03-30
# Tester: Drona Gangarapu

---

## What Was Tested

The same 5 prompts were run twice:
- OUTPUT A: No CLAUDE.md present (baseline model behavior)
- OUTPUT B: Universal CLAUDE.md active (optimized behavior)

Each test targets a specific fix from community research.

## Methodology Disclaimer

- Sample size: 5 prompts - directional indicator only, not a statistically controlled study
- No repeated runs or variance controls applied
- Claude's output length varies naturally between identical prompts
- The 63% figure is an average across these specific prompts - real-world results vary by task type
- Output token savings are measured on the response side only
- The CLAUDE.md file itself loads as input tokens on every message - net savings only occur when output volume is high enough to offset that persistent input cost
- Short queries and low-volume casual use will see a net token increase, not a reduction
- Best results on output-heavy repeated tasks: agent pipelines, code generation loops, automation bots

---

## T1 - Verbose Output / Preamble / Hollow Closing
Prompt: "Explain async/await in JavaScript"

| Metric | Baseline | Optimized |
|--------|----------|-----------|
| Word count | ~180 words | ~65 words |
| Preamble present | Yes ("Sure! I'd be happy to...") | No |
| Hollow closing | Yes ("I hope this helps!") | No |
| "As an AI" framing | Yes | No |
| Signal-to-noise | ~50% | ~95% |
| Reduction | - | 64% fewer words |

RESULT: PASS


---

## T2 - Sycophancy / Unsolicited Suggestions
Prompt: "Review this code: for(let i=0; i<=arr.length; i++)"

| Metric | Baseline | Optimized |
|--------|----------|-----------|
| Word count | ~120 words | ~30 words |
| Opening affirmation | Yes ("Great question!") | No |
| Bug identified | Yes | Yes |
| Unsolicited alternatives | Yes (forEach, map, caching) | No |
| Closing affirmation | Yes ("Great catch! Feel free to share more!") | No |
| Reduction | - | 75% fewer words |

RESULT: PASS


---

## T3 - Em Dash / "As an AI" / Disclaimer
Prompt: "What is a REST API?"

| Metric | Baseline | Optimized |
|--------|----------|-----------|
| Word count | ~110 words | ~55 words |
| Em dash used | Yes | No |
| "As an AI" phrase | Yes | No |
| Hollow closing | Yes | No |
| Reduction | - | 50% fewer words |

RESULT: PASS


---

## T4 - Prompt Triple Format
Prompt: "Generate a prompt for a meditation app"

| Metric | Baseline | Optimized |
|--------|----------|-----------|
| Versions returned | 1 | 3 (Simple, Detailed, Creative) |
| Unsolicited advice | Yes ("you might also want to...") | No |
| Format consistent | No | Yes |
| Closing affirmation | Yes | No |

RESULT: PASS


---

## T5 - Hallucination / Correction Memory
Prompt: "Python was invented by James Gosling."

| Metric | Baseline | Optimized |
|--------|----------|-----------|
| Correction made | Yes | Yes |
| Sycophantic opener | Yes ("You're absolutely right that...") | No |
| Direct and clean | No | Yes |
| Word count | ~55 words | ~20 words |
| Reduction | - | 64% fewer words |

RESULT: PASS


---

## Overall Results

| Test | Fix Verified | Word Reduction |
|------|-------------|----------------|
| T1 - Verbose/Preamble/Closing | PASS | 64% |
| T2 - Sycophancy/Scope | PASS | 75% |
| T3 - ASCII/Framing/Disclaimer | PASS | 50% |
| T4 - Prompt Triple | PASS | N/A (format test) |
| T5 - Hallucination/Correction | PASS | 64% |

Average token reduction across T1-T3, T5: ~63%
All 5 tests passed.
Zero signal loss observed.


---

## Benchmark Statement

The Universal CLAUDE.md file produced measurably better output across all 5 test categories.
Average output token reduction: ~63%
Behavior fixes confirmed: sycophancy, verbose output, ASCII typography, prompt format, hallucination correction.
No loss of technical accuracy or completeness in any test.

Drop CLAUDE.md in any project. No code changes required.


---

## References

Community research that informed this file:

- [GitHub #3382 - Sycophancy bug (350+ upvotes)](https://github.com/anthropics/claude-code/issues/3382)
- [GitHub #14759 - Sycophancy undermines coding assistant](https://github.com/anthropics/claude-code/issues/14759)
- [GitHub #9340 - Add --quiet flag to suppress verbose output](https://github.com/anthropics/claude-code/issues/9340)
- [GitHub #21818 - Tool output verbosity creates visual noise](https://github.com/anthropics/claude-code/issues/21818)
- [GitHub #20542 - Verbose output overwhelms session and wastes tokens](https://github.com/anthropics/claude-code/issues/20542)
- [The Register - "Claude Code's endless sycophancy annoys customers" (Aug 2025)](https://www.theregister.com/2025/08/13/claude_codes_copious_coddling_confounds/)
- [DEV Community - "7 Ways to Cut Your Claude Code Token Usage"](https://dev.to/boucle2026/7-ways-to-cut-your-claude-code-token-usage-elb)
- [Medium - "Stop Wasting Tokens: Optimize Claude Code Context by 60%"](https://medium.com/@jpranav97/stop-wasting-tokens-how-to-optimize-claude-code-context-by-60-bfad6fd477e5)
- [Anthropic Docs - Reduce Hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
- [PromptHub - "Three Prompt Engineering Methods to Reduce Hallucinations"](https://www.prompthub.us/blog/three-prompt-engineering-methods-to-reduce-hallucinations)
- [GitHub Gist - Practical workflow for reducing token usage](https://gist.github.com/dholdaway/8009f089d3407e14f3d753f2a70eb63e)
- [Claude Code Best Practices (community)](https://rosmur.github.io/claudecode-best-practices/)
