# CLAUDE.md benchmark (directional)

- model: `haiku`  runs/cell: 5
- metric: mean output tokens per prompt (word count in parens)
- baseline condition: `baseline` (no CLAUDE.md)

| Prompt | baseline | CLAUDE.md |
|---|---|---|
| T1-async | 685 (278w) | 649 (269w) -5% |
| T2-review | 338 (58w) | 365 (54w) +8% |
| T3-rest | 452 (214w) | 415 (174w) -8% |
| T4-prompt | 507 (247w) | 509 (242w) +0% |
| T5-halluc | 261 (47w) | 289 (35w) +11% |
| **total tok** | **2244** | **2227** **-1%** |

- baseline total cost: $0.0849
- CLAUDE.md total cost: $0.0865

> Directional only: single-session means, output varies run-to-run. Negative % = fewer output tokens than baseline.