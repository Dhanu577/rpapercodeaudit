# DESeq2 evaluation

## Inputs and matching method

The supplied `DESeq.txt` uploads were byte-identical and were processed against DESeq2 commit `76c5f8523716804dbe0a9500b4b7e216c6af225c`. The supplied workbook contains 107 rows on `Combined Table`; 85 rows contain explicit source-code file and line-range references. The tool output contains 319 accepted claims and 1,595 validated keyword candidate locations.

For this comparison, a table reference is parsed from patterns such as `R/core.R:745–786` and normalized to repository-relative paths. An **exact match** requires the same path and exactly the same inclusive start/end lines. An **overlap match** requires the same path and intersecting inclusive line ranges. The overlap measure is more informative here because the tool deliberately returns a small context window around keyword hits, while the table cites larger explanatory ranges. Rows without explicit file/range references cannot match by this method.

## Requested numbers

| Measure | Result |
|---|---:|
| (a) My paper-claim rows found by the tool | **16 of 107** using overlap matching; **0 of 107** using exact matching |
| (b) Tool locations matching mine | **11 of 1,595** using overlap matching; **0 of 1,595** using exact matching |
| (c) Rows where the tool said `not found` but the table says implemented | **0** direct tool `not_found` rows: the no-API run returned 0 not-found claims. Because the table has no shared claim IDs with the heuristic output, rows with no reference overlap are not relabeled as tool `not found`. |
| (d) False locations | **1,584 of 1,595** tool locations had no overlap with a supplied table reference. These are more precisely **unmatched candidates**, not proven false locations, because the table contains only 85 explicit references and the tool is intentionally keyword-based. |

The tool run itself produced:

- 319 accepted claims;
- 0 rejected claims;
- 1,595 validated locations;
- 0 invalid/discarded excerpts;
- 0 `not_found` claims.

The high candidate count and the unmatched-candidate count are reported without inflation. They should not be interpreted as detection accuracy, precision, or recall. The comparison is limited by the table’s missing paper-sentence fields, different claim granularity, and incomplete explicit file/range references.
