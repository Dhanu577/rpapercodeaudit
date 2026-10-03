# Adversarial validator benchmark v2

## Scope and safety

This benchmark exercises only the project's real deterministic validator functions: `validate_claims()` from `rpapercodeaudit/claim_extraction.py`, `prepare_repository()` and `validate_location()` from `rpapercodeaudit/code_location.py`. All repositories and text files are synthetic. It does not use or execute DESeq2 or its fixture repository. The v1 cases, checksum, and result files are not inputs to this benchmark and must remain unchanged.

Each case exercises one validator independently. Sentence cases send the paper text and claim items to `validate_claims()`. Commit cases pass the declared object/ref and `checkout` flag to `prepare_repository()`. Location cases pass the repo fixture and item mapping to `validate_location()`. The runner records the function's raw error text and does not recreate its checks.

## Labels, fixed before execution

- **must_accept**: the documented behavior clearly says the validator accepts the input.
- **must_reject**: the documented behavior clearly says the validator rejects the input.
- **boundary**: the documented behavior does not clearly determine the outcome. Boundary observations are recorded for review only and are excluded from false-acceptance/false-rejection counts.

Sentence labels use the documented rule: accept an exact sentence substring after whitespace normalization; there is no case folding, punctuation normalization, stemming, or edit distance. Boundary items such as Unicode normalization, zero-width characters, empty text, and short substrings are not relabeled based on observed results. Commit boundary labels reflect unspecified resolution of abbreviations/symbolic refs and the documented `checkout=False` HEAD-match requirement. Location boundary labels cover host filesystem, newline, type-coercion, binary/empty-file, and indexing-scope questions that are not specified by the exact excerpt contract.

`generate_cases_v2.py` assigns labels from its static mutation-type table before any result is observed. The rationale is stored per case. There are at least 10 cases per mutation type; the result report flags types with fewer than 20 cases.

## Build synthetic fixtures and generate frozen inputs

Run these steps before the benchmark. They only create small static text files and synthetic Git metadata. The builder creates temporary content under the ignored `benchmark/fixtures/build/` directory and a task-specific external target under `/tmp/benchmark-adversarial-v2-outside/`. The generator creates an isolated Git worktree for every commit case so `checkout=True` cannot affect another case's `checkout=False` result.

```bash
python3 benchmark/fixtures/build_fixtures.py
python3 benchmark/generate_cases_v2.py
```

The generator uses seed 42. Verify `cases_v2.jsonl` and `cases_v2.sha256` are committed before any valid-checksum run. The runner refuses a checksum mismatch.

## Freeze-before-run sequence

1. Commit and push the fixtures, generator, cases/checksum, README, tests, and runner to the v2 branch.
2. Create and push the annotated tag `benchmark-cases-v2-frozen` on that commit.
3. Only after the tag exists, run the validators and generate the reports.

```bash
python3 benchmark/run_validator_v2.py
python3 benchmark/compute_metrics_v2.py
pytest -q benchmark/tests/test_v2_benchmark.py
```

## Outputs

- `cases_v2.jsonl`, `cases_v2.sha256`: frozen inputs and checksum.
- `results_v2.jsonl`: one result per case, including expected class, raw validator inputs, observed outcome, validator name, and raw error.
- `metrics_v2.csv`: must-accept/must-reject acceptance and rejection rates with Wilson 95% intervals clipped to `[0, 1]`.
- `per_type_v2.csv`: sample counts, accepted/rejected counts, observed-versus-expected summary, and an `n < 20` flag per mutation type.
- `boundary_findings.md`: boundary observations only, with no false-acceptance/rejection score.
- `bugs_found.md`: every must-accept rejection and must-reject acceptance, including inputs, raw log, and a hypothesis; labels are never edited to hide a result.
- `REPORT_v2.md`: methods, rates, mutation tables, bugs, boundary summary, platform, and limitations.
