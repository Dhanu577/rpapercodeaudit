# Benchmark anomalies

## Comparison with v1

All 422 frozen cases were rerun in both deterministic and LLM-assisted modes. For comparison, the three v1 location fields (`file_exists`, `line_range_valid`, and `excerpt_matches`) were treated as a single location outcome: true only when all three were true. The v1 first-failure fields for those three checks were mapped to the consolidated `location` stage.

| Mode | Cases compared | Final-decision disagreements | Stage-outcome disagreements | Mapped first-failure disagreements |
|---|---:|---:|---:|---:|
| deterministic | 422 | 0 | 0 | 0 |
| llm_assisted | 422 | 0 | 0 | 0 |

There are no case-level disagreements to enumerate. No case labels or expected outcomes were changed. The frozen `cases.jsonl` SHA-256 remains `22e1fd85202e08adadd5eb9b974ff83532811e3b29e1a447cf324d5904a4343d`.

## Label consistency

False acceptances/rejections against Tier A expected labels: **0** (0 false acceptances; 0 false rejections).
