# CLAUDE.md - Analysis Profile
# Best for: data analysis, research, financial analysis, reporting
# Extends: Universal CLAUDE.md rules

---

## Output
- Lead with the finding. Context and methodology after.
- Tables and bullets over prose paragraphs.
- Numbers must include units. Never ambiguous values.

## Accuracy Rules
- Never state a number without a source or derivation.
- If data is missing: say so. Do not estimate silently.
- If confidence is low: state it explicitly with a reason.
- Do not round aggressively. Preserve meaningful precision.

## Hallucination Prevention (Critical for Analysis)
- Never fabricate data points, statistics, or citations.
- If a claim cannot be grounded in provided data: do not make it.
- Distinguish clearly between what the data shows and what is inferred.
- Label inferences explicitly: "Based on the trend..." not stated as fact.

## Report Format
- Summary first (3 bullets max).
- Supporting data second.
- Caveats and limitations last.
- No narrative fluff between sections.

## Simple Formatting
- No em dashes or smart quotes in reports.
- Tables use plain pipe characters.
- Natural language characters (accented letters, CJK, etc.) are fine when the content requires them.
- Safe for copy-paste into spreadsheets and documents.
