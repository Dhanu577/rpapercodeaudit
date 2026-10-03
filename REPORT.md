# RPaperCodeAudit citation-integrity benchmark report

## Scope and inspection result

This benchmark evaluates the **mechanical citation-integrity layer** of RPaperCodeAudit using DESeq2 at commit `76c5f8523716804dbe0a9500b4b7e216c6af225c`. The audited package was treated as static text. No R, C++, package installation script, or repository code was executed.

The existing implementation has two related validators rather than one unified validator. `claim_extraction.validate_claims()` normalizes whitespace and requires each proposed paper sentence to be an exact substring; it rejects malformed or non-matching claims independently. `code_location.prepare_repository()` resolves and optionally checks out a requested commit. `build_index()` indexes text under `R/`, `src/`, `man/`, `vignettes/`, and `tests/`. `validate_location()` checks repository containment, file readability, line-range validity, and exact excerpt equality. The pipeline does not expose these as an independent stage log, so this benchmark uses a thin wrapper without modifying decision logic.

The LLM extraction path and deterministic path converge on the same exact paper-sentence validator. LLM-assisted ranking can change candidate ordering, but mechanical validation remains separate. The seeded benchmark therefore runs the same frozen cases in both mode labels; the natural LLM proposal run is skipped because no API key was configured.

## Frozen benchmark

The case file contains **422 cases** generated with seed `42` and frozen by SHA-256 checksum:

`22e1fd85202e08adadd5eb9b974ff83532811e3b29e1a447cf324d5904a4343d`

| Tier | Cases | Expected interpretation |
|---|---:|---|
| A | 326 | Mechanical benchmark; A0 valid, A1–A5 invalid |
| B | 96 | Authentic but semantically out-of-scope evidence |

Tier A coverage was: A0 valid 24, A1 altered sentence 72, A2 nonexistent sentence 72, A3 wrong commit 15, A4 wrong file 23, and A5 invalid line range 120. A3 is below the target of 20 because only 15 source rows had an available historical commit whose cited text differed; the generator skipped other wrong-commit cases rather than inventing them. A4 has 23 cases because one source row had no suitable alternate text file with a compatible line range.

## Seeded results

| Metric | Result | Wilson 95% CI | n |
|---|---:|---:|---:|
| Acceptance rate for valid records | 100.0% | 86.2–100.0% | 24 |
| False-rejection rate | 0.0% | 0.0–13.8% | 24 |
| Rejection rate for invalid records | 100.0% | 98.7–100.0% | 302 |
| False-acceptance rate | 0.0% | 0.0–1.3% | 302 |

The seeded deterministic and LLM-assisted result files were identical after excluding the mode label. There were **zero false acceptances, zero false rejections, and zero anomalies**.

### First-failure stages

| First failing stage | Cases |
|---|---:|
| `sentence_match` | 144 |
| `repo_commit_valid` | 15 |
| `file_exists` | 24 |
| `line_range_valid` | 48 |
| `excerpt_matches` | 71 |

The runner evaluates all stages independently even when an earlier stage fails. Across all cases, stage failures were observed at `sentence_match` 144 times, `repo_commit_valid` 15 times, `file_exists` 24 times, `line_range_valid` 72 times, and `excerpt_matches` 158 times. These are any-stage counts and can overlap.

## Tier B scope boundary

All 96 Tier B cases were mechanically accepted: 24 each for irrelevant authentic excerpts, misleading justifications, contradictory authentic excerpts, and compound-claim interpretations. This is expected. The mechanical layer verifies citation integrity; it does not assess semantic relevance, whether the excerpt supports the full claim, or whether the implementation is scientifically consistent with the paper.

## Natural proposals

The deterministic heuristic extractor proposed **319** records, all 319 passed its exact paper-sentence validation, and 0 were rejected at that stage. The natural-proposal summary explicitly notes that source-location validation requires explicit evidence records; extractor proposals alone do not contain a file, line range, or excerpt.

The LLM-assisted natural proposal run was **skipped** because no LLM API key was configured. No model output was simulated.

## Conclusion

The validator rejected **100.0%** of mechanically invalid proposals (n = 302; 95% CI 98.7–100.0%) and retained **100.0%** of valid ones (n = 24; 95% CI 86.2–100.0%). It does not assess semantic relevance, and accepted **100.0%** of semantically irrelevant or contradictory but authentic excerpts in the Tier B boundary cases (n = 96), which is the intended boundary of the mechanical layer.

## Anomalies and limitations

No false acceptance or false rejection occurred in the seeded cases, so `benchmark/anomalies.md` contains an empty anomaly list. The A3 category is under the requested 20-case target because the repository history did not provide enough differing historical blobs for all 24 source rows; this was reported rather than padded. The natural proposal pass is claim-level because extraction output does not itself contain source evidence. The benchmark therefore does not establish that a natural proposal would receive a valid code citation without a subsequent location stage. Results are specific to the supplied 24-row DESeq2 evidence set and the frozen commit.

## Reproduction

```bash
cd /home/ubuntu/RPaperCodeAudit
python3 benchmark/generate_cases.py
python3 benchmark/run_validator.py --mode deterministic
python3 benchmark/run_validator.py --mode llm_assisted
python3 benchmark/run_validator.py --natural
python3 benchmark/compute_metrics.py
python3 -m pytest -q benchmark/tests
```

The benchmark outputs include JSONL case/results files, CSV metric tables, `anomalies.md`, two figures under `benchmark/figures/`, and the frozen checksum. The website work is paused and is not part of this benchmark.
