# Validator adversarial benchmark v3

V3 is a static, spec-labeled test set for the project's real validators. Its labels are frozen before any v3 validator run; observed output never changes a case label.

## Contract and protected inputs

- `VALIDATOR_SPEC.md` is the authoritative acceptance contract.
- `investigation_v3.md` records the v2 observations used to document unchanged boundaries.
- `min_words_impact.md` lists the saved natural proposals with fewer than five normalized tokens; it is a static analysis, not a validator result.
- `cases_v3.jsonl` and `cases_v3.sha256` are the frozen inputs. Do not edit or regenerate either after the annotated tag `benchmark-cases-v3-frozen` is pushed.
- The v1 files `cases.jsonl`, `cases.sha256`, `results*.jsonl`, `metrics*.csv`, `REPORT*.md`, and `anomalies.md`, and the v2 `cases_v2.jsonl`, `cases_v2.sha256`, `results_v2.jsonl`, `REPORT_v2.md`, and other existing v2 result artifacts are preserved. V3 and rerun outputs use new filenames.
- Every v3 case is executed against exactly one real function: `validate_claims`, `prepare_repository`, or `validate_location`. The runner only decodes the JSON representation of the deliberate Python-int-subclass boundary input; it does not reproduce validation logic.

## Classes

- `must_accept`: the spec requires acceptance.
- `must_reject`: the spec requires rejection.
- `boundary`: behavior is explicitly documented as unchanged, but is not scored as a required decision.

Every mutation type has at least 10 cases. `S_unicode_composition` is labeled from the declared code-point rule: NFC exact text accepts and an NFD variant against NFC paper text rejects. The synthetic subclass line-number value is encoded as a typed JSON object and reconstructed by the runner solely to test Python's `int` subclass behavior.

## Fixture setup and freeze

The fixture builder creates static text repositories and Git objects; it does not run project validators. To recreate ignored working fixtures, run from the repository root:

```bash
python3 benchmark/fixtures/build_fixtures.py
python3 benchmark/generate_cases_v2.py --output /tmp/cases_v2_runtime/cases_v2.jsonl
python3 benchmark/generate_cases_v3.py
sha256sum -c benchmark/cases_v3.sha256
```

Review and commit the spec, investigation, implementation, tests, v3 generator, runner, frozen cases, checksum, and this README as the first commit. Push that commit and create the annotated `benchmark-cases-v3-frozen` tag before running tests or any validator benchmark. The runner refuses a checksum mismatch:

```bash
python3 benchmark/run_validator_v3.py --output benchmark/results_v3.jsonl
```

The v3 output and subsequent comparison reports must use new filenames; frozen v1/v2 inputs and result artifacts must not be overwritten.
