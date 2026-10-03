# V3.1 preflight checks (before case freeze)

This preflight was completed after changing the sentence rule and before creating the v3.1 freeze tag. **No v3/v3.1 case was evaluated.**

| Check | Result |
|---|---:|
| Original valid Tier-A pilot records | 24/24 accepted by the v1 wrapper (sentence, repository, and location stages) |
| Saved deterministic natural proposals | 319 accepted, 0 rejected by `validate_claims` |
| `short_sentence` report flag (`<5` normalized whitespace tokens) | 193/319 |
| `reference_like` report flag | 114/319 |
| Both report-only flags | 95/319 |
| Neither report-only flag | 107/319 |

Flags do not affect the validator result. `reference_like` is a report heuristic for numeric-only values/ranges, numbered reference prefixes, numeric bracket citations, author-year citations, DOI/URL/PMID/ISBN markers, and explicit reference/bibliography headings. Per-item values are in `natural_proposals_v3_1_flags.csv`; counts are in `natural_proposals_v3_1_summary.json`.

The regenerated case inventory is 580 cases: 125 `must_accept`, 375 `must_reject`, and 80 `boundary`. It has 58 mutation types, at least 10 cases each. This is the count of frozen input labels, not observed validator results.

The 24-record pilot used a temporary subset and temporary clone under `/tmp`; it did not modify the stored v1 cases, checksum, or DESeq2 working clone. The 319-proposal analysis used the saved deterministic input and the project's `validate_claims()` function.
