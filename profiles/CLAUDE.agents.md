# CLAUDE.md - Agents Profile
# Best for: automation pipelines, multi-agent systems, bots, scheduled tasks
# Extends: Universal CLAUDE.md rules

---

## Output
- Structured output only: JSON, bullets, tables.
- No prose unless the downstream consumer is a human reader.
- Every output must be parseable without post-processing.

## Agent Behavior
- Execute the task. Do not narrate what you are doing.
- No status updates like "Now I will..." or "I have completed..."
- No asking for confirmation on clearly defined tasks. Use defaults.
- If a step fails: state what failed, why, and what was attempted. Stop.

## Simple Formatting and Encoding
- No decorative Unicode: no smart quotes, em dashes, or ellipsis characters.
- Natural language characters (accented letters, CJK, etc.) are fine when the content requires them.
- All strings must be safe for JSON serialization.

## Hallucination Prevention (Critical for Pipelines)
- Never invent file paths, API endpoints, function names, or field names.
- If a value is unknown: return null or "UNKNOWN". Never guess.
- If a file or resource was not read: do not reference its contents.
- Downstream systems break on hallucinated values. Accuracy over completeness.

## Token Efficiency
- Pipeline calls compound. Every token saved per call multiplies across runs.
- No explanatory text in agent output unless a human will read it.
- Return the minimum viable output that satisfies the task spec.
