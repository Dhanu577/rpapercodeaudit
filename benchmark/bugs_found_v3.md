# v3 bugs and must-class failures — v3 cases not run

The frozen v3 case set was not executed because the explicit `MIN_WORDS = 5` natural-proposal impact gate fired first. Therefore no must-class v3 case failures were observed, and no v3 benchmark bug count can be reported.

## Original pilot positive rejected by the new sentence rule

| Case | Expected | Observed | Validator log | Hypothesis |
|---|---|---|---|---|
| `row-6-A0` (`source_record_id: row-6`) | Accept; original Tier-A valid record | Rejected at `sentence_match`; repository and location stages passed | `verbatim_sentence must contain at least 5 words after whitespace normalization (found 4)` | The extracted paper text is a four-token fragment (`Theestimate of theLFCpriorwidthiscalculatedas follows.`). This is a direct consequence of the specified five-word threshold, not a repository or location failure. |

This pilot failure is also listed in `min_words_impact.md`; it is not mislabeled as a v3 benchmark observation.
