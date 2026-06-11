# CLAUDE.md benchmark (directional)

- model: `opus`  runs/cell: 5
- metric: mean output tokens per prompt (word count in parens)
- baseline condition: `baseline` (no CLAUDE.md)

| Prompt | baseline | CLAUDE.md |
|---|---|---|
| T1-async | 958 (401w) | 771 (320w) -20% |
| T2-review | 364 (135w) | 330 (130w) -9% |
| T3-rest | 753 (320w) | 667 (274w) -11% |
| T4-prompt | 637 (319w) | 877 (305w) +38% |
| T5-halluc | 138 (46w) | 109 (27w) -21% |
| **total tok** | **2851** | **2753** **-3%** |

- baseline total cost: $0.2731
- CLAUDE.md total cost: $0.2797

> Directional only: single-session means, output varies run-to-run. Negative % = fewer output tokens than baseline.