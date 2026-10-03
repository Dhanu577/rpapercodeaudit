# Adversarial validator benchmark v3.1

## Methods

The v3.1 cases were regenerated from seed 42, checksum-frozen, pushed, and tagged before this run. Sentence cases call `validate_claims()`, commit cases call `prepare_repository()`, and location cases call `validate_location()`. The runner performs no duplicate validation checks. No labels were changed after observing results.

Cases: **580** — `must_accept` **125**, `must_reject` **375**, `boundary` **80**. Validator accepted **180** total cases.

## Acceptance/rejection rates (Wilson 95% CI)

| Expected class | n | Acceptance rate | 95% CI | Rejection rate | 95% CI |
|---|---|---|---|---|---|
| must_accept | 125 | 1.000 | [0.970, 1.000] | 0.000 | [0.000, 0.030] |
| must_reject | 375 | 0.000 | [0.000, 0.010] | 1.000 | [0.990, 1.000] |

Boundary cases are excluded from these rates and are reported only as observed in `boundary_findings_v3_1.md`.

## Per mutation type

| Group | Mutation type | Class | n | Accepted | Rejected | Observed vs expected |
|---|---|---|---|---|---|---|
| commit | C_39_character_hash | must_reject | 10 | 0 | 10 | all_match |
| commit | C_41_character_hash | must_reject | 10 | 0 | 10 | all_match |
| commit | C_HEAD | must_reject | 10 | 0 | 10 | all_match |
| commit | C_HEAD_parent | must_reject | 10 | 0 | 10 | all_match |
| commit | C_ambiguous_short_hash | must_reject | 10 | 0 | 10 | all_match |
| commit | C_branch_name | must_reject | 10 | 0 | 10 | all_match |
| commit | C_empty_hash | must_reject | 10 | 0 | 10 | all_match |
| commit | C_foreign_repository_hash | must_reject | 10 | 0 | 10 | all_match |
| commit | C_full_hash | must_accept | 10 | 10 | 0 | all_match |
| commit | C_nonexistent_hash | must_reject | 10 | 0 | 10 | all_match |
| commit | C_nonhex_40_character_hash | must_reject | 10 | 0 | 10 | all_match |
| commit | C_random_hex | must_reject | 10 | 0 | 10 | all_match |
| commit | C_short_hash | must_reject | 10 | 0 | 10 | all_match |
| commit | C_tag_name | must_reject | 10 | 0 | 10 | all_match |
| commit | C_uppercase_hash | must_accept | 10 | 10 | 0 | all_match |
| location | L_absolute_outside | must_reject | 10 | 0 | 10 | all_match |
| location | L_binary_file | boundary | 10 | 0 | 10 | observed_only |
| location | L_correct_multiline | must_accept | 10 | 10 | 0 | all_match |
| location | L_correct_single_line | must_accept | 10 | 10 | 0 | all_match |
| location | L_crlf_lf | boundary | 10 | 5 | 5 | observed_only |
| location | L_directory_not_file | must_reject | 10 | 0 | 10 | all_match |
| location | L_duplicate_code_two_places | must_accept | 10 | 10 | 0 | all_match |
| location | L_empty_file | must_reject | 10 | 0 | 10 | all_match |
| location | L_end_beyond_eof | must_reject | 10 | 0 | 10 | all_match |
| location | L_filename_case | boundary | 10 | 5 | 5 | observed_only |
| location | L_int_subclass_line_number | boundary | 10 | 10 | 0 | observed_only |
| location | L_large_line_number | must_reject | 10 | 0 | 10 | all_match |
| location | L_line_number_coercion | must_reject | 10 | 0 | 10 | all_match |
| location | L_missing_keys | must_reject | 10 | 0 | 10 | all_match |
| location | L_no_final_newline | must_accept | 10 | 10 | 0 | all_match |
| location | L_none_values | must_reject | 10 | 0 | 10 | all_match |
| location | L_nonexistent_file | must_reject | 10 | 0 | 10 | all_match |
| location | L_nonpositive_start | must_reject | 10 | 0 | 10 | all_match |
| location | L_outside_indexed_directories | boundary | 10 | 10 | 0 | observed_only |
| location | L_partial_excerpt | must_reject | 10 | 0 | 10 | all_match |
| location | L_path_traversal | must_reject | 10 | 0 | 10 | all_match |
| location | L_same_text_different_file | must_accept | 10 | 10 | 0 | all_match |
| location | L_start_after_end | must_reject | 10 | 0 | 10 | all_match |
| location | L_superset_excerpt | must_reject | 10 | 0 | 10 | all_match |
| location | L_symlink_outside | must_reject | 10 | 0 | 10 | all_match |
| location | L_tab_vs_spaces | boundary | 10 | 5 | 5 | observed_only |
| location | L_trailing_whitespace | must_reject | 10 | 0 | 10 | all_match |
| sentence | S_changed_case | must_reject | 10 | 0 | 10 | all_match |
| sentence | S_changed_punctuation | must_reject | 10 | 0 | 10 | all_match |
| sentence | S_duplicate_sentence | must_accept | 10 | 10 | 0 | all_match |
| sentence | S_empty_or_whitespace | must_reject | 10 | 0 | 10 | all_match |
| sentence | S_exactly_five_words | must_accept | 10 | 10 | 0 | all_match |
| sentence | S_extra_whitespace | must_accept | 10 | 10 | 0 | all_match |
| sentence | S_extra_word | must_reject | 10 | 0 | 10 | all_match |
| sentence | S_four_word_sentence | boundary | 10 | 10 | 0 | observed_only |
| sentence | S_hyphen_variants | must_reject | 10 | 0 | 10 | all_match |
| sentence | S_nonbreaking_space | must_accept | 10 | 10 | 0 | all_match |
| sentence | S_one_word_substring | boundary | 10 | 10 | 0 | observed_only |
| sentence | S_sentence_boundary | must_accept | 10 | 10 | 0 | all_match |
| sentence | S_smart_quotes | must_reject | 10 | 0 | 10 | all_match |
| sentence | S_unicode_composition | must_accept | 5 | 5 | 0 | all_match |
| sentence | S_unicode_composition | must_reject | 5 | 0 | 5 | all_match |
| sentence | S_word_removed_or_reordered | must_reject | 10 | 0 | 10 | all_match |
| sentence | S_zero_width_character | must_reject | 10 | 0 | 10 | all_match |

Distinct mutation types: **58**; types with n < 20: **58**.

Must-class failures: **0**. See `bugs_found_v3.md`. Boundary cases: **80**.

## Pilot, natural proposals, and report-only flags

The preflight accepted all **24/24** original valid pilot records. The saved natural deterministic proposals were **319 accepted / 0 rejected**. Short sentences (<5 normalized whitespace tokens): **193**; reference-like heuristic: **114**; both: **95**. These are report-only flags and do not influence validator decisions. See `natural_proposals_v3_1_flags.csv`.

## v1/v2 regressions

Every changed v1 stage/final decision and every changed v2 acceptance outcome is listed in `regression_report.md`. New results are kept in `results_v1_on_v3validator.jsonl` and `results_v2_on_v3validator.jsonl` without overwriting prior outputs.

## Limitations

- OS/platform: `Linux-6.18.38+-x86_64-with-glibc2.39`; Python `3.12.3`.
- Project-authored unit tests do not independently establish semantic correctness.
- The synthetic benchmark uses at least 10 cases per mutation type; several groups are still small.
- File-name case observations are specific to the tested Linux filesystem.
- Natural proposal flags are heuristic report annotations, not semantic classifications or validator rules.
