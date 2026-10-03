# Adversarial validator benchmark v2

## Methods

Cases were generated from seed 42 and frozen with a SHA-256 checksum before any validator run. Sentence cases call the project's `validate_claims()`; commit cases call `prepare_repository()` with their declared `checkout` value; location cases call `validate_location()`. The runner records each function's output or raw error. It does not reproduce checks locally. DESeq2 and its fixture repository are not used or executed; all repository and file inputs are synthetic static text.

Cases: **520** total — must_accept **80**, must_reject **220**, boundary **220**. Overall accepted by the called function: **215**.

## Acceptance/rejection rates (Wilson 95% CI)

| Expected class | n | Acceptance rate | 95% CI | Rejection rate | 95% CI |
|---|---|---|---|---|---|
| must_accept | 80 | 1.000 | [0.954, 1.000] | 0.000 | [0.000, 0.046] |
| must_reject | 220 | 0.000 | [0.000, 0.017] | 1.000 | [0.983, 1.000] |

Boundary cases are reported as observations only and are not included in these rates.

## Per mutation type

| Group | Mutation type | Class | n | Accepted | Rejected | Observed vs expected |
|---|---|---|---|---|---|---|
| commit | C_HEAD | boundary | 10 | 10 | 0 | observed_only |
| commit | C_HEAD_parent | boundary | 10 | 5 | 5 | observed_only |
| commit | C_ambiguous_short_hash | boundary | 10 | 0 | 10 | observed_only |
| commit | C_branch_name | boundary | 10 | 10 | 0 | observed_only |
| commit | C_empty_hash | must_reject | 10 | 0 | 10 | all_match |
| commit | C_foreign_repository_hash | must_reject | 10 | 0 | 10 | all_match |
| commit | C_full_hash | must_accept | 10 | 10 | 0 | all_match |
| commit | C_nonexistent_hash | must_reject | 10 | 0 | 10 | all_match |
| commit | C_random_hex | must_reject | 10 | 0 | 10 | all_match |
| commit | C_short_hash | boundary | 10 | 10 | 0 | observed_only |
| commit | C_tag_name | boundary | 10 | 10 | 0 | observed_only |
| commit | C_uppercase_hash | boundary | 10 | 10 | 0 | observed_only |
| location | L_absolute_outside | must_reject | 10 | 0 | 10 | all_match |
| location | L_binary_file | boundary | 10 | 0 | 10 | observed_only |
| location | L_correct_multiline | must_accept | 10 | 10 | 0 | all_match |
| location | L_correct_single_line | must_accept | 10 | 10 | 0 | all_match |
| location | L_crlf_lf | boundary | 10 | 5 | 5 | observed_only |
| location | L_directory_not_file | must_reject | 10 | 0 | 10 | all_match |
| location | L_duplicate_code_two_places | must_accept | 10 | 10 | 0 | all_match |
| location | L_empty_file | boundary | 10 | 0 | 10 | observed_only |
| location | L_end_beyond_eof | must_reject | 10 | 0 | 10 | all_match |
| location | L_filename_case | boundary | 10 | 5 | 5 | observed_only |
| location | L_large_line_number | boundary | 10 | 0 | 10 | observed_only |
| location | L_line_number_coercion | boundary | 10 | 10 | 0 | observed_only |
| location | L_missing_keys | must_reject | 10 | 0 | 10 | all_match |
| location | L_no_final_newline | boundary | 10 | 10 | 0 | observed_only |
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
| location | L_trailing_whitespace | boundary | 10 | 0 | 10 | observed_only |
| sentence | S_changed_case | must_reject | 10 | 0 | 10 | all_match |
| sentence | S_changed_punctuation | must_reject | 10 | 0 | 10 | all_match |
| sentence | S_duplicate_sentence | must_accept | 10 | 10 | 0 | all_match |
| sentence | S_empty_or_whitespace | boundary | 10 | 10 | 0 | observed_only |
| sentence | S_extra_whitespace | must_accept | 10 | 10 | 0 | all_match |
| sentence | S_extra_word | must_reject | 10 | 0 | 10 | all_match |
| sentence | S_hyphen_variants | must_reject | 10 | 0 | 10 | all_match |
| sentence | S_nonbreaking_space | boundary | 10 | 10 | 0 | observed_only |
| sentence | S_one_word_substring | boundary | 10 | 10 | 0 | observed_only |
| sentence | S_sentence_boundary | must_accept | 10 | 10 | 0 | all_match |
| sentence | S_smart_quotes | must_reject | 10 | 0 | 10 | all_match |
| sentence | S_unicode_composition | boundary | 10 | 5 | 5 | observed_only |
| sentence | S_word_removed_or_reordered | must_reject | 10 | 0 | 10 | all_match |
| sentence | S_zero_width_character | boundary | 10 | 0 | 10 | observed_only |

Mutation types with n < 20: **52** (all generated types have n ≥ 10; see `per_type_v2.csv` for flags).

## Bugs and boundaries

Must-accept rejections or must-reject acceptances: **0**. See `bugs_found.md` for case inputs, raw logs, and hypotheses. Boundary cases: **220**; see `boundary_findings.md` for observed behavior.

## Platform and limitations

- OS/platform: `Linux-6.18.38+-x86_64-with-glibc2.39`.
- Python: `3.12.3`.
- File-name case behavior is tested on the filesystem hosting this run; boundary observations should not be generalized to all filesystems.
- These tests establish only observed validator behavior on the frozen synthetic inputs, not semantic correctness or behavior for every possible path or Git reference.
- The generated repository contains synthetic text and Git metadata only; no fixture code was executed.
