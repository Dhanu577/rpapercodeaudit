# Boundary findings

Boundary labels were assigned before running the validators and are not scored as false acceptances or false rejections. This file records observed behavior only.

## Summary by mutation type

| Mutation type | n | Accepted | Rejected |
|---|---|---|---|
| C_HEAD | 10 | 10 | 0 |
| C_HEAD_parent | 10 | 5 | 5 |
| C_ambiguous_short_hash | 10 | 0 | 10 |
| C_branch_name | 10 | 10 | 0 |
| C_short_hash | 10 | 10 | 0 |
| C_tag_name | 10 | 10 | 0 |
| C_uppercase_hash | 10 | 10 | 0 |
| L_binary_file | 10 | 0 | 10 |
| L_crlf_lf | 10 | 5 | 5 |
| L_empty_file | 10 | 0 | 10 |
| L_filename_case | 10 | 5 | 5 |
| L_large_line_number | 10 | 0 | 10 |
| L_line_number_coercion | 10 | 10 | 0 |
| L_no_final_newline | 10 | 10 | 0 |
| L_outside_indexed_directories | 10 | 10 | 0 |
| L_tab_vs_spaces | 10 | 5 | 5 |
| L_trailing_whitespace | 10 | 0 | 10 |
| S_empty_or_whitespace | 10 | 10 | 0 |
| S_nonbreaking_space | 10 | 10 | 0 |
| S_one_word_substring | 10 | 10 | 0 |
| S_unicode_composition | 10 | 5 | 5 |
| S_zero_width_character | 10 | 0 | 10 |

## Per-case observations

| Case | Mutation type | Observed | Validator | Raw error |
|---|---|---|---|---|
| C_branch_name-03-checkout-true | C_branch_name | accepted | prepare_repository | — |
| C_uppercase_hash-01-checkout-true | C_uppercase_hash | accepted | prepare_repository | — |
| L-trailing-05 | L_trailing_whitespace | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| S-one-word-09 | S_one_word_substring | accepted | validate_claims | — |
| S-zero-width-05 | S_zero_width_character | rejected | validate_claims | verbatim_sentence is not an exact substring after whitespace normalization |
| L-tab-spaces-00 | L_tab_vs_spaces | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| L-name-case-00 | L_filename_case | rejected | validate_location | invalid location: [Errno 2] No such file or directory: '/home/ubuntu/rpapercodeaudit/benchmark/fixtures/build/source_repo/R/Sample.txt' |
| C_uppercase_hash-04-checkout-true | C_uppercase_hash | accepted | prepare_repository | — |
| S-zero-width-06 | S_zero_width_character | rejected | validate_claims | verbatim_sentence is not an exact substring after whitespace normalization |
| C_short_hash-03-checkout-true | C_short_hash | accepted | prepare_repository | — |
| S-one-word-01 | S_one_word_substring | accepted | validate_claims | — |
| L-empty-file-01 | L_empty_file | rejected | validate_location | invalid location: line range 1-1 is outside file with 0 lines |
| C_HEAD_parent-01-checkout-false | C_HEAD_parent | rejected | prepare_repository | HEAD 0af07405ae264da39239e8b6044217c84ca03a6c does not match requested commit 7aa5a93386344b1b6d964b76a7f72690314f5801 |
| C_ambiguous_short_hash-00-checkout-false | C_ambiguous_short_hash | rejected | prepare_repository | git rev-parse --verify eb47^{commit} failed: error: short object ID eb47 is ambiguous hint: The candidates are: hint:   eb4748d commit 2001-01-01 - ambiguous-prefix-probe-85 hint:   eb477f7 commit 2001-01-01 - ambiguous-prefix-probe-82 fatal: Needed a single revision |
| L-no-final-newline-04 | L_no_final_newline | accepted | validate_location | — |
| S-nbsp-06 | S_nonbreaking_space | accepted | validate_claims | — |
| L-name-case-04 | L_filename_case | rejected | validate_location | invalid location: [Errno 2] No such file or directory: '/home/ubuntu/rpapercodeaudit/benchmark/fixtures/build/source_repo/R/Sample.txt' |
| S-nbsp-02 | S_nonbreaking_space | accepted | validate_claims | — |
| L-empty-file-07 | L_empty_file | rejected | validate_location | invalid location: line range 1-1 is outside file with 0 lines |
| C_short_hash-00-checkout-true | C_short_hash | accepted | prepare_repository | — |
| S-zero-width-00 | S_zero_width_character | rejected | validate_claims | verbatim_sentence is not an exact substring after whitespace normalization |
| C_HEAD-00-checkout-false | C_HEAD | accepted | prepare_repository | — |
| S-nbsp-03 | S_nonbreaking_space | accepted | validate_claims | — |
| C_HEAD-03-checkout-true | C_HEAD | accepted | prepare_repository | — |
| L-no-final-newline-00 | L_no_final_newline | accepted | validate_location | — |
| L-empty-file-00 | L_empty_file | rejected | validate_location | invalid location: line range 1-1 is outside file with 0 lines |
| L-line-type-07 | L_line_number_coercion | accepted | validate_location | — |
| L-line-type-05 | L_line_number_coercion | accepted | validate_location | — |
| C_uppercase_hash-03-checkout-false | C_uppercase_hash | accepted | prepare_repository | — |
| S-empty-00 | S_empty_or_whitespace | accepted | validate_claims | — |
| L-large-line-01 | L_large_line_number | rejected | validate_location | invalid location: line range 1000001-1000001 is outside file with 20 lines |
| C_branch_name-02-checkout-false | C_branch_name | accepted | prepare_repository | — |
| L-outside-index-07 | L_outside_indexed_directories | accepted | validate_location | — |
| L-outside-index-04 | L_outside_indexed_directories | accepted | validate_location | — |
| S-nbsp-00 | S_nonbreaking_space | accepted | validate_claims | — |
| C_short_hash-04-checkout-false | C_short_hash | accepted | prepare_repository | — |
| C_ambiguous_short_hash-03-checkout-false | C_ambiguous_short_hash | rejected | prepare_repository | git rev-parse --verify 4b2c^{commit} failed: error: short object ID 4b2c is ambiguous hint: The candidates are: hint:   4b2c41f commit 2001-01-01 - ambiguous-prefix-probe-287 hint:   4b2ce71 commit 2001-01-01 - ambiguous-prefix-probe-811 fatal: Needed a single revision |
| C_HEAD_parent-03-checkout-false | C_HEAD_parent | rejected | prepare_repository | HEAD d9b31994651624e2f3290738f5c49e947c7448f8 does not match requested commit 5965a996e88ce9413ac762219af1a7985faf6088 |
| L-large-line-05 | L_large_line_number | rejected | validate_location | invalid location: line range 1000005-1000005 is outside file with 20 lines |
| C_tag_name-03-checkout-false | C_tag_name | accepted | prepare_repository | — |
| C_HEAD-03-checkout-false | C_HEAD | accepted | prepare_repository | — |
| L-name-case-01 | L_filename_case | accepted | validate_location | — |
| S-one-word-02 | S_one_word_substring | accepted | validate_claims | — |
| C_tag_name-04-checkout-true | C_tag_name | accepted | prepare_repository | — |
| L-outside-index-00 | L_outside_indexed_directories | accepted | validate_location | — |
| L-crlf-01 | L_crlf_lf | accepted | validate_location | — |
| L-line-type-02 | L_line_number_coercion | accepted | validate_location | — |
| L-crlf-05 | L_crlf_lf | accepted | validate_location | — |
| L-tab-spaces-07 | L_tab_vs_spaces | accepted | validate_location | — |
| S-empty-07 | S_empty_or_whitespace | accepted | validate_claims | — |
| C_tag_name-00-checkout-true | C_tag_name | accepted | prepare_repository | — |
| C_tag_name-01-checkout-false | C_tag_name | accepted | prepare_repository | — |
| S-nbsp-05 | S_nonbreaking_space | accepted | validate_claims | — |
| L-binary-01 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| C_short_hash-04-checkout-true | C_short_hash | accepted | prepare_repository | — |
| L-outside-index-03 | L_outside_indexed_directories | accepted | validate_location | — |
| C_branch_name-03-checkout-false | C_branch_name | accepted | prepare_repository | — |
| L-binary-09 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| L-line-type-00 | L_line_number_coercion | accepted | validate_location | — |
| S-nbsp-04 | S_nonbreaking_space | accepted | validate_claims | — |
| L-large-line-02 | L_large_line_number | rejected | validate_location | invalid location: line range 1000002-1000002 is outside file with 20 lines |
| S-empty-09 | S_empty_or_whitespace | accepted | validate_claims | — |
| C_uppercase_hash-00-checkout-false | C_uppercase_hash | accepted | prepare_repository | — |
| C_HEAD-02-checkout-false | C_HEAD | accepted | prepare_repository | — |
| L-binary-07 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| S-one-word-03 | S_one_word_substring | accepted | validate_claims | — |
| L-no-final-newline-09 | L_no_final_newline | accepted | validate_location | — |
| L-trailing-00 | L_trailing_whitespace | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| L-no-final-newline-07 | L_no_final_newline | accepted | validate_location | — |
| L-no-final-newline-03 | L_no_final_newline | accepted | validate_location | — |
| L-outside-index-05 | L_outside_indexed_directories | accepted | validate_location | — |
| C_HEAD_parent-02-checkout-true | C_HEAD_parent | accepted | prepare_repository | — |
| L-binary-06 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| S-one-word-00 | S_one_word_substring | accepted | validate_claims | — |
| L-name-case-06 | L_filename_case | rejected | validate_location | invalid location: [Errno 2] No such file or directory: '/home/ubuntu/rpapercodeaudit/benchmark/fixtures/build/source_repo/R/Sample.txt' |
| L-crlf-09 | L_crlf_lf | accepted | validate_location | — |
| C_ambiguous_short_hash-04-checkout-false | C_ambiguous_short_hash | rejected | prepare_repository | git rev-parse --verify 7f2c^{commit} failed: error: short object ID 7f2c is ambiguous hint: The candidates are: hint:   7f2c891 commit 2001-01-01 - ambiguous-prefix-probe-513 hint:   7f2ca95 commit 2001-01-01 - ambiguous-prefix-probe-850 fatal: Needed a single revision |
| C_branch_name-00-checkout-false | C_branch_name | accepted | prepare_repository | — |
| L-tab-spaces-04 | L_tab_vs_spaces | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| C_HEAD-00-checkout-true | C_HEAD | accepted | prepare_repository | — |
| C_uppercase_hash-01-checkout-false | C_uppercase_hash | accepted | prepare_repository | — |
| L-binary-03 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| L-crlf-02 | L_crlf_lf | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| L-empty-file-08 | L_empty_file | rejected | validate_location | invalid location: line range 1-1 is outside file with 0 lines |
| L-tab-spaces-06 | L_tab_vs_spaces | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| C_ambiguous_short_hash-01-checkout-false | C_ambiguous_short_hash | rejected | prepare_repository | git rev-parse --verify 23ea^{commit} failed: error: short object ID 23ea is ambiguous hint: The candidates are: hint:   23ea452 commit 2001-01-01 - ambiguous-prefix-probe-148 hint:   23eafb8 commit 2001-01-01 - ambiguous-prefix-probe-286 fatal: Needed a single revision |
| C_ambiguous_short_hash-00-checkout-true | C_ambiguous_short_hash | rejected | prepare_repository | git rev-parse --verify eb47^{commit} failed: error: short object ID eb47 is ambiguous hint: The candidates are: hint:   eb4748d commit 2001-01-01 - ambiguous-prefix-probe-85 hint:   eb477f7 commit 2001-01-01 - ambiguous-prefix-probe-82 fatal: Needed a single revision |
| S-nbsp-09 | S_nonbreaking_space | accepted | validate_claims | — |
| L-crlf-00 | L_crlf_lf | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| C_uppercase_hash-02-checkout-false | C_uppercase_hash | accepted | prepare_repository | — |
| C_HEAD-04-checkout-false | C_HEAD | accepted | prepare_repository | — |
| L-large-line-03 | L_large_line_number | rejected | validate_location | invalid location: line range 1000003-1000003 is outside file with 20 lines |
| C_short_hash-01-checkout-true | C_short_hash | accepted | prepare_repository | — |
| L-tab-spaces-08 | L_tab_vs_spaces | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| L-no-final-newline-06 | L_no_final_newline | accepted | validate_location | — |
| L-no-final-newline-01 | L_no_final_newline | accepted | validate_location | — |
| C_HEAD-02-checkout-true | C_HEAD | accepted | prepare_repository | — |
| C_ambiguous_short_hash-03-checkout-true | C_ambiguous_short_hash | rejected | prepare_repository | git rev-parse --verify 4b2c^{commit} failed: error: short object ID 4b2c is ambiguous hint: The candidates are: hint:   4b2c41f commit 2001-01-01 - ambiguous-prefix-probe-287 hint:   4b2ce71 commit 2001-01-01 - ambiguous-prefix-probe-811 fatal: Needed a single revision |
| S-unicode-03 | S_unicode_composition | accepted | validate_claims | — |
| C_branch_name-01-checkout-false | C_branch_name | accepted | prepare_repository | — |
| S-unicode-08 | S_unicode_composition | rejected | validate_claims | verbatim_sentence is not an exact substring after whitespace normalization |
| L-binary-00 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| L-large-line-09 | L_large_line_number | rejected | validate_location | invalid location: line range 1000009-1000009 is outside file with 20 lines |
| L-line-type-03 | L_line_number_coercion | accepted | validate_location | — |
| L-name-case-02 | L_filename_case | rejected | validate_location | invalid location: [Errno 2] No such file or directory: '/home/ubuntu/rpapercodeaudit/benchmark/fixtures/build/source_repo/R/Sample.txt' |
| L-trailing-04 | L_trailing_whitespace | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| S-zero-width-03 | S_zero_width_character | rejected | validate_claims | verbatim_sentence is not an exact substring after whitespace normalization |
| L-outside-index-09 | L_outside_indexed_directories | accepted | validate_location | — |
| L-large-line-08 | L_large_line_number | rejected | validate_location | invalid location: line range 1000008-1000008 is outside file with 20 lines |
| C_HEAD_parent-00-checkout-false | C_HEAD_parent | rejected | prepare_repository | HEAD 7aa5a93386344b1b6d964b76a7f72690314f5801 does not match requested commit 06c4bb86ee456eca5c1cca9d9a4bc2ae96fe56df |
| L-binary-08 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| C_uppercase_hash-00-checkout-true | C_uppercase_hash | accepted | prepare_repository | — |
| L-trailing-01 | L_trailing_whitespace | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| C_branch_name-00-checkout-true | C_branch_name | accepted | prepare_repository | — |
| L-binary-04 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| S-nbsp-07 | S_nonbreaking_space | accepted | validate_claims | — |
| C_ambiguous_short_hash-04-checkout-true | C_ambiguous_short_hash | rejected | prepare_repository | git rev-parse --verify 7f2c^{commit} failed: error: short object ID 7f2c is ambiguous hint: The candidates are: hint:   7f2c891 commit 2001-01-01 - ambiguous-prefix-probe-513 hint:   7f2ca95 commit 2001-01-01 - ambiguous-prefix-probe-850 fatal: Needed a single revision |
| S-empty-04 | S_empty_or_whitespace | accepted | validate_claims | — |
| C_HEAD-01-checkout-true | C_HEAD | accepted | prepare_repository | — |
| S-zero-width-09 | S_zero_width_character | rejected | validate_claims | verbatim_sentence is not an exact substring after whitespace normalization |
| L-trailing-08 | L_trailing_whitespace | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| S-empty-01 | S_empty_or_whitespace | accepted | validate_claims | — |
| L-name-case-08 | L_filename_case | rejected | validate_location | invalid location: [Errno 2] No such file or directory: '/home/ubuntu/rpapercodeaudit/benchmark/fixtures/build/source_repo/R/Sample.txt' |
| L-empty-file-09 | L_empty_file | rejected | validate_location | invalid location: line range 1-1 is outside file with 0 lines |
| S-unicode-05 | S_unicode_composition | accepted | validate_claims | — |
| C_tag_name-00-checkout-false | C_tag_name | accepted | prepare_repository | — |
| C_branch_name-02-checkout-true | C_branch_name | accepted | prepare_repository | — |
| S-zero-width-02 | S_zero_width_character | rejected | validate_claims | verbatim_sentence is not an exact substring after whitespace normalization |
| L-empty-file-05 | L_empty_file | rejected | validate_location | invalid location: line range 1-1 is outside file with 0 lines |
| L-large-line-07 | L_large_line_number | rejected | validate_location | invalid location: line range 1000007-1000007 is outside file with 20 lines |
| C_HEAD-01-checkout-false | C_HEAD | accepted | prepare_repository | — |
| L-tab-spaces-09 | L_tab_vs_spaces | accepted | validate_location | — |
| C_HEAD-04-checkout-true | C_HEAD | accepted | prepare_repository | — |
| L-tab-spaces-03 | L_tab_vs_spaces | accepted | validate_location | — |
| S-empty-03 | S_empty_or_whitespace | accepted | validate_claims | — |
| S-empty-02 | S_empty_or_whitespace | accepted | validate_claims | — |
| L-large-line-06 | L_large_line_number | rejected | validate_location | invalid location: line range 1000006-1000006 is outside file with 20 lines |
| C_short_hash-00-checkout-false | C_short_hash | accepted | prepare_repository | — |
| L-outside-index-01 | L_outside_indexed_directories | accepted | validate_location | — |
| L-crlf-03 | L_crlf_lf | accepted | validate_location | — |
| L-line-type-08 | L_line_number_coercion | accepted | validate_location | — |
| C_HEAD_parent-04-checkout-false | C_HEAD_parent | rejected | prepare_repository | HEAD 922ef9ff5e1b19f1a5a15f0bc18130f0b9180241 does not match requested commit d9b31994651624e2f3290738f5c49e947c7448f8 |
| S-nbsp-01 | S_nonbreaking_space | accepted | validate_claims | — |
| C_HEAD_parent-03-checkout-true | C_HEAD_parent | accepted | prepare_repository | — |
| L-tab-spaces-02 | L_tab_vs_spaces | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| C_branch_name-01-checkout-true | C_branch_name | accepted | prepare_repository | — |
| L-name-case-09 | L_filename_case | accepted | validate_location | — |
| L-empty-file-03 | L_empty_file | rejected | validate_location | invalid location: line range 1-1 is outside file with 0 lines |
| L-crlf-08 | L_crlf_lf | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| L-line-type-04 | L_line_number_coercion | accepted | validate_location | — |
| L-crlf-06 | L_crlf_lf | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| S-empty-08 | S_empty_or_whitespace | accepted | validate_claims | — |
| C_tag_name-04-checkout-false | C_tag_name | accepted | prepare_repository | — |
| C_short_hash-02-checkout-false | C_short_hash | accepted | prepare_repository | — |
| C_short_hash-03-checkout-false | C_short_hash | accepted | prepare_repository | — |
| L-empty-file-04 | L_empty_file | rejected | validate_location | invalid location: line range 1-1 is outside file with 0 lines |
| L-empty-file-06 | L_empty_file | rejected | validate_location | invalid location: line range 1-1 is outside file with 0 lines |
| L-name-case-07 | L_filename_case | accepted | validate_location | — |
| C_HEAD_parent-01-checkout-true | C_HEAD_parent | accepted | prepare_repository | — |
| L-name-case-05 | L_filename_case | accepted | validate_location | — |
| C_ambiguous_short_hash-02-checkout-true | C_ambiguous_short_hash | rejected | prepare_repository | git rev-parse --verify a5ff^{commit} failed: error: short object ID a5ff is ambiguous hint: The candidates are: hint:   a5ff365 commit 2001-01-01 - ambiguous-prefix-probe-737 hint:   a5ffba8 commit 2001-01-01 - ambiguous-prefix-probe-79 fatal: Needed a single revision |
| C_uppercase_hash-04-checkout-false | C_uppercase_hash | accepted | prepare_repository | — |
| S-one-word-04 | S_one_word_substring | accepted | validate_claims | — |
| L-outside-index-02 | L_outside_indexed_directories | accepted | validate_location | — |
| S-empty-06 | S_empty_or_whitespace | accepted | validate_claims | — |
| L-line-type-09 | L_line_number_coercion | accepted | validate_location | — |
| C_tag_name-02-checkout-true | C_tag_name | accepted | prepare_repository | — |
| C_ambiguous_short_hash-01-checkout-true | C_ambiguous_short_hash | rejected | prepare_repository | git rev-parse --verify 23ea^{commit} failed: error: short object ID 23ea is ambiguous hint: The candidates are: hint:   23ea452 commit 2001-01-01 - ambiguous-prefix-probe-148 hint:   23eafb8 commit 2001-01-01 - ambiguous-prefix-probe-286 fatal: Needed a single revision |
| C_HEAD_parent-02-checkout-false | C_HEAD_parent | rejected | prepare_repository | HEAD 5965a996e88ce9413ac762219af1a7985faf6088 does not match requested commit 0af07405ae264da39239e8b6044217c84ca03a6c |
| S-zero-width-08 | S_zero_width_character | rejected | validate_claims | verbatim_sentence is not an exact substring after whitespace normalization |
| S-one-word-07 | S_one_word_substring | accepted | validate_claims | — |
| C_ambiguous_short_hash-02-checkout-false | C_ambiguous_short_hash | rejected | prepare_repository | git rev-parse --verify a5ff^{commit} failed: error: short object ID a5ff is ambiguous hint: The candidates are: hint:   a5ff365 commit 2001-01-01 - ambiguous-prefix-probe-737 hint:   a5ffba8 commit 2001-01-01 - ambiguous-prefix-probe-79 fatal: Needed a single revision |
| L-large-line-00 | L_large_line_number | rejected | validate_location | invalid location: line range 1000000-1000000 is outside file with 20 lines |
| S-unicode-07 | S_unicode_composition | accepted | validate_claims | — |
| L-no-final-newline-05 | L_no_final_newline | accepted | validate_location | — |
| S-one-word-08 | S_one_word_substring | accepted | validate_claims | — |
| L-trailing-09 | L_trailing_whitespace | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| C_tag_name-03-checkout-true | C_tag_name | accepted | prepare_repository | — |
| L-binary-02 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| S-empty-05 | S_empty_or_whitespace | accepted | validate_claims | — |
| L-line-type-06 | L_line_number_coercion | accepted | validate_location | — |
| L-trailing-06 | L_trailing_whitespace | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| L-no-final-newline-08 | L_no_final_newline | accepted | validate_location | — |
| S-one-word-06 | S_one_word_substring | accepted | validate_claims | — |
| S-zero-width-07 | S_zero_width_character | rejected | validate_claims | verbatim_sentence is not an exact substring after whitespace normalization |
| L-crlf-07 | L_crlf_lf | accepted | validate_location | — |
| C_tag_name-01-checkout-true | C_tag_name | accepted | prepare_repository | — |
| L-empty-file-02 | L_empty_file | rejected | validate_location | invalid location: line range 1-1 is outside file with 0 lines |
| L-binary-05 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| L-outside-index-06 | L_outside_indexed_directories | accepted | validate_location | — |
| L-trailing-07 | L_trailing_whitespace | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| L-line-type-01 | L_line_number_coercion | accepted | validate_location | — |
| S-unicode-06 | S_unicode_composition | rejected | validate_claims | verbatim_sentence is not an exact substring after whitespace normalization |
| S-nbsp-08 | S_nonbreaking_space | accepted | validate_claims | — |
| L-tab-spaces-01 | L_tab_vs_spaces | accepted | validate_location | — |
| L-name-case-03 | L_filename_case | accepted | validate_location | — |
| L-crlf-04 | L_crlf_lf | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| C_short_hash-01-checkout-false | C_short_hash | accepted | prepare_repository | — |
| C_tag_name-02-checkout-false | C_tag_name | accepted | prepare_repository | — |
| S-one-word-05 | S_one_word_substring | accepted | validate_claims | — |
| L-trailing-03 | L_trailing_whitespace | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| C_short_hash-02-checkout-true | C_short_hash | accepted | prepare_repository | — |
| L-outside-index-08 | L_outside_indexed_directories | accepted | validate_location | — |
| S-unicode-00 | S_unicode_composition | rejected | validate_claims | verbatim_sentence is not an exact substring after whitespace normalization |
| L-no-final-newline-02 | L_no_final_newline | accepted | validate_location | — |
| C_uppercase_hash-03-checkout-true | C_uppercase_hash | accepted | prepare_repository | — |
| L-tab-spaces-05 | L_tab_vs_spaces | accepted | validate_location | — |
| L-large-line-04 | L_large_line_number | rejected | validate_location | invalid location: line range 1000004-1000004 is outside file with 20 lines |
| C_branch_name-04-checkout-false | C_branch_name | accepted | prepare_repository | — |
| S-unicode-02 | S_unicode_composition | rejected | validate_claims | verbatim_sentence is not an exact substring after whitespace normalization |
| C_uppercase_hash-02-checkout-true | C_uppercase_hash | accepted | prepare_repository | — |
| S-zero-width-01 | S_zero_width_character | rejected | validate_claims | verbatim_sentence is not an exact substring after whitespace normalization |
| C_HEAD_parent-04-checkout-true | C_HEAD_parent | accepted | prepare_repository | — |
| S-unicode-09 | S_unicode_composition | accepted | validate_claims | — |
| S-unicode-01 | S_unicode_composition | accepted | validate_claims | — |
| L-trailing-02 | L_trailing_whitespace | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| S-zero-width-04 | S_zero_width_character | rejected | validate_claims | verbatim_sentence is not an exact substring after whitespace normalization |
| C_branch_name-04-checkout-true | C_branch_name | accepted | prepare_repository | — |
| C_HEAD_parent-00-checkout-true | C_HEAD_parent | accepted | prepare_repository | — |
| S-unicode-04 | S_unicode_composition | rejected | validate_claims | verbatim_sentence is not an exact substring after whitespace normalization |
