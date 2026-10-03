# Validator adversarial benchmark v3.1

V3.1 is a static, spec-labeled test set for the project's real validators. Its labels are frozen before any v3.1 validator run; observed output never changes a case label.

## Contract and protected inputs

- `VALIDATOR_SPEC.md` is the authoritative acceptance contract.
- `investigation_v3.md` records the v2 observations used to document unchanged boundaries.
- `min_words_impact.md` is the historical impact record for the superseded five-word rule. V3.1 accepts any non-empty exact substring regardless of token count.
- `cases_v3.jsonl` and `cases_v3.sha256` are the v3.1 frozen inputs. Do not edit or regenerate either after the annotated tag `benchmark-cases-v3.1-frozen` is pushed. The earlier `benchmark-cases-v3-frozen` tag remains unchanged.
- The v1 files `cases.jsonl`, `cases.sha256`, `results*.jsonl`, `metrics*.csv`, `REPORT*.md`, and `anomalies.md`, and the v2 `cases_v2.jsonl`, `cases_v2.sha256`, `results_v2.jsonl`, `REPORT_v2.md`, and other existing v2 result artifacts are preserved. V3 and rerun outputs use new filenames.
- Every v3 case is executed against exactly one real function: `validate_claims`, `prepare_repository`, or `validate_location`. The runner only decodes the JSON representation of the deliberate Python-int-subclass boundary input; it does not reproduce validation logic.

## Classes

- `must_accept`: the spec requires acceptance.
- `must_reject`: the spec requires rejection.
- `boundary`: behavior is explicitly documented as unchanged, but is not scored as a required decision.

Every mutation type has at least 10 cases. `S_unicode_composition` is labeled from the declared code-point rule: NFC exact text accepts and an NFD variant against NFC paper text rejects. The synthetic subclass line-number value is encoded as a typed JSON object and reconstructed by the runner solely to test Python's `int` subclass behavior.

## V3.1 relabeling and report-only flags

`S_empty_or_whitespace` remains `must_reject`; `S_one_word_substring` and `S_four_word_sentence` are `boundary` (observed behavior only); `S_exactly_five_words` remains `must_accept`. This correction follows the `min_words_impact.md` review: token count is unreliable for PDF-derived text and reference-list fragments, so shortness no longer determines acceptance. The natural-proposal analysis reports `short_sentence` (<5 normalized whitespace tokens) and `reference_like` flags and counts, but neither flag rejects a claim.

`reference_like` is a transparent heuristic for report triage only: numeric-only values/ranges, numbered reference prefixes, numeric bracket citations, author-year citations, DOI/URL/PMID/ISBN markers, and explicit reference/bibliography headings are flagged. It is not a validator rule.

## Fixture setup and freeze

The fixture builder creates static text repositories and Git objects; it does not run project validators. To recreate ignored working fixtures, run from the repository root:

```bash
python3 benchmark/fixtures/build_fixtures.py
python3 benchmark/generate_cases_v2.py --output /tmp/cases_v2_runtime/cases_v2.jsonl
python3 benchmark/generate_cases_v3.py
(cd benchmark && sha256sum -c cases_v3.sha256)
```

Review and commit the revised spec, case relabeling, implementation, tests, v3.1 generator/analysis, runner, cases, checksum, and this README. Push the commit and create the annotated `benchmark-cases-v3.1-frozen` tag **before running any v3.1 case**. The runner refuses a checksum mismatch:

```bash
python3 benchmark/run_validator_v3.py --cases benchmark/cases_v3.jsonl --output benchmark/results_v3_1.jsonl
```

The v3 output and subsequent comparison reports must use new filenames; frozen v1/v2 inputs and result artifacts must not be overwritten.
