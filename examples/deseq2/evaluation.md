# DESeq2 evaluation

## Inputs and run status

The requested DESeq2 commit was verified successfully as `76c5f8523716804dbe0a9500b4b7e216c6af225c`. The supplied Methods text was processed in default no-API mode. The comparison workbook `deseq2_pilot_combined_table.xlsx` was not present in the current workspace, so table matching could not be performed.

The tool produced **319 accepted paper claims**, **1,595 validated keyword locations**, **0 not-found claims**, and **0 invalid excerpts**. These are pipeline counts, not accuracy measurements; the keyword mode intentionally returns conservative candidates.

## Requested comparison

| Measure | Count |
|---|---:|
| Paper-claim rows found by the tool | 319 of 319 accepted claims had at least one validated location |
| Tool locations matching the user's table | N/A — comparison workbook missing |
| Rows marked not found by tool but implemented in user's table | N/A — comparison workbook missing |
| False locations | N/A — comparison workbook missing |

No claims about detection accuracy are made. Once the workbook is supplied, compare canonicalized repository-relative file paths and inclusive line ranges at commit `76c5f8523716804dbe0a9500b4b7e216c6af225c`.
