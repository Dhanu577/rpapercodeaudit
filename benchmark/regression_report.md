# Regression report — not run

The requested v1 (422-case) and v2 (520-case) full regression comparisons against the new validator were **not run**. The required post-freeze natural-proposal check confirmed that `MIN_WORDS = 5` rejects 193 of the 319 saved deterministic proposals, which triggered the explicit STOP instruction before v3 benchmark execution and v1/v2 regression runs.

Accordingly, this report contains no changed-case list and makes no claim that changes are limited to the specified gap types. The separate 24-record original pilot check is documented in `min_words_impact.md` and `REPORT_v3.md`.
