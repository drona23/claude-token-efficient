# CLAUDE.md benchmark (directional)

- model: `sonnet`  runs/cell: 5
- metric: mean output tokens per prompt (word count in parens)
- baseline condition: `baseline` (no CLAUDE.md)

| Prompt | baseline | CLAUDE.md |
|---|---|---|
| T1-async | 566 (276w) | 517 (251w) -9% |
| T2-review | 190 (51w) | 215 (46w) +13% |
| T3-rest | 301 (173w) | 285 (167w) -5% |
| T4-prompt | 489 (239w) | 360 (215w) -26% |
| T5-halluc | 113 (28w) | 97 (22w) -15% |
| **total tok** | **1659** | **1473** **-11%** |

- baseline total cost: $0.2366
- CLAUDE.md total cost: $0.2363

> Directional only: single-session means, output varies run-to-run. Negative % = fewer output tokens than baseline.