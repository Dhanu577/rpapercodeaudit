# Validator benchmark v3.1 — preflight complete, case run pending

## Status

The v3.1 sentence rule and case labels have been revised after the historical `MIN_WORDS = 5` impact check. Short non-empty exact substrings are accepted; empty/whitespace-only text is rejected. The v3.1 cases have been regenerated and checksum-verified but **have not been run**. The new annotated freeze tag must be pushed first.

## Preflight checks

| Check | Result |
|---|---:|
| Original valid Tier-A pilot records | 24/24 accepted by all v1 wrapper stages |
| Saved deterministic proposals | 319 accepted, 0 rejected by `validate_claims` |
| `short_sentence` report-only flag (<5 normalized tokens) | 193 |
| `reference_like` report-only flag | 114 |
| Both flags | 95 |
| Neither flag | 107 |

The flags are descriptive only and do not reject proposals. The `reference_like` heuristic covers numeric-only values/ranges, numbered reference prefixes, numeric bracket citations, author-year citations, DOI/URL/PMID/ISBN markers, and explicit reference/bibliography headings. Per-proposal flags and counts are in `natural_proposals_v3_1_flags.csv` and `natural_proposals_v3_1_summary.json`.

## Frozen case inventory (labels, not observed outcomes)

| Class | Cases |
|---|---:|
| `must_accept` | 125 |
| `must_reject` | 375 |
| `boundary` | 80 |
| **Total** | **580** |

The set has 58 mutation types with at least 10 cases each. See `CASE_RELABELING_v3_1.md` for the sentence-case changes and rationale.

## Pending after the freeze tag

The v3.1 case results, acceptance/rejection rates and Wilson intervals, boundary observations, must-class bug log, and v1/v2 regressions are intentionally absent at this stage. They will be produced only after `benchmark-cases-v3.1-frozen` is pushed. This file is a preflight status, not a benchmark result.

## Limitations

The report-layer `reference_like` flag is heuristic, not a semantic classifier. The pilot and natural-proposal checks use project-authored validation logic. The synthetic benchmark has small per-type samples, and platform findings apply to Linux.
