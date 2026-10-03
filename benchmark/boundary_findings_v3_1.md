# V3.1 boundary findings

Boundary cases were labeled before the run and are reported as observations only; they are excluded from must-class rates.

## By mutation type

| Mutation type | n | Accepted | Rejected |
|---|---|---|---|
| L_binary_file | 10 | 0 | 10 |
| L_crlf_lf | 10 | 5 | 5 |
| L_filename_case | 10 | 5 | 5 |
| L_int_subclass_line_number | 10 | 10 | 0 |
| L_outside_indexed_directories | 10 | 10 | 0 |
| L_tab_vs_spaces | 10 | 5 | 5 |
| S_four_word_sentence | 10 | 10 | 0 |
| S_one_word_substring | 10 | 10 | 0 |

## Per-case observations

| Case | Mutation type | Observed | Validator | Raw error |
|---|---|---|---|---|
| L-binary-02 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| S-one-word-05 | S_one_word_substring | accepted | validate_claims | — |
| L-binary-08 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| L-binary-07 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| L-tab-spaces-03 | L_tab_vs_spaces | accepted | validate_location | — |
| L-outside-index-01 | L_outside_indexed_directories | accepted | validate_location | — |
| L-tab-spaces-00 | L_tab_vs_spaces | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| S-one-word-06 | S_one_word_substring | accepted | validate_claims | — |
| L-crlf-09 | L_crlf_lf | accepted | validate_location | — |
| L-outside-index-06 | L_outside_indexed_directories | accepted | validate_location | — |
| L-tab-spaces-06 | L_tab_vs_spaces | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| S-one-word-01 | S_one_word_substring | accepted | validate_claims | — |
| S-four-word-08 | S_four_word_sentence | accepted | validate_claims | — |
| L-int-subclass-09 | L_int_subclass_line_number | accepted | validate_location | — |
| S-four-word-07 | S_four_word_sentence | accepted | validate_claims | — |
| S-four-word-01 | S_four_word_sentence | accepted | validate_claims | — |
| L-tab-spaces-09 | L_tab_vs_spaces | accepted | validate_location | — |
| L-tab-spaces-01 | L_tab_vs_spaces | accepted | validate_location | — |
| L-tab-spaces-08 | L_tab_vs_spaces | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| L-name-case-08 | L_filename_case | rejected | validate_location | invalid location: [Errno 2] No such file or directory: '/home/ubuntu/rpapercodeaudit/benchmark/fixtures/build/source_repo/R/Sample.txt' |
| L-name-case-02 | L_filename_case | rejected | validate_location | invalid location: [Errno 2] No such file or directory: '/home/ubuntu/rpapercodeaudit/benchmark/fixtures/build/source_repo/R/Sample.txt' |
| L-int-subclass-05 | L_int_subclass_line_number | accepted | validate_location | — |
| L-tab-spaces-04 | L_tab_vs_spaces | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| S-one-word-08 | S_one_word_substring | accepted | validate_claims | — |
| L-binary-04 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| S-one-word-07 | S_one_word_substring | accepted | validate_claims | — |
| S-four-word-04 | S_four_word_sentence | accepted | validate_claims | — |
| L-name-case-00 | L_filename_case | rejected | validate_location | invalid location: [Errno 2] No such file or directory: '/home/ubuntu/rpapercodeaudit/benchmark/fixtures/build/source_repo/R/Sample.txt' |
| L-binary-00 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| L-crlf-00 | L_crlf_lf | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| S-one-word-03 | S_one_word_substring | accepted | validate_claims | — |
| L-outside-index-04 | L_outside_indexed_directories | accepted | validate_location | — |
| L-name-case-06 | L_filename_case | rejected | validate_location | invalid location: [Errno 2] No such file or directory: '/home/ubuntu/rpapercodeaudit/benchmark/fixtures/build/source_repo/R/Sample.txt' |
| L-name-case-03 | L_filename_case | accepted | validate_location | — |
| L-int-subclass-01 | L_int_subclass_line_number | accepted | validate_location | — |
| L-outside-index-08 | L_outside_indexed_directories | accepted | validate_location | — |
| L-tab-spaces-02 | L_tab_vs_spaces | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| L-outside-index-07 | L_outside_indexed_directories | accepted | validate_location | — |
| L-crlf-07 | L_crlf_lf | accepted | validate_location | — |
| L-crlf-03 | L_crlf_lf | accepted | validate_location | — |
| S-four-word-05 | S_four_word_sentence | accepted | validate_claims | — |
| L-crlf-04 | L_crlf_lf | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| S-four-word-03 | S_four_word_sentence | accepted | validate_claims | — |
| S-four-word-06 | S_four_word_sentence | accepted | validate_claims | — |
| L-binary-01 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| L-outside-index-09 | L_outside_indexed_directories | accepted | validate_location | — |
| L-binary-03 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| S-four-word-00 | S_four_word_sentence | accepted | validate_claims | — |
| L-int-subclass-08 | L_int_subclass_line_number | accepted | validate_location | — |
| L-name-case-05 | L_filename_case | accepted | validate_location | — |
| L-outside-index-00 | L_outside_indexed_directories | accepted | validate_location | — |
| L-outside-index-02 | L_outside_indexed_directories | accepted | validate_location | — |
| L-int-subclass-04 | L_int_subclass_line_number | accepted | validate_location | — |
| L-name-case-09 | L_filename_case | accepted | validate_location | — |
| L-outside-index-05 | L_outside_indexed_directories | accepted | validate_location | — |
| L-crlf-06 | L_crlf_lf | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| L-binary-06 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| L-outside-index-03 | L_outside_indexed_directories | accepted | validate_location | — |
| L-tab-spaces-07 | L_tab_vs_spaces | accepted | validate_location | — |
| L-binary-05 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| L-int-subclass-07 | L_int_subclass_line_number | accepted | validate_location | — |
| L-crlf-05 | L_crlf_lf | accepted | validate_location | — |
| L-name-case-01 | L_filename_case | accepted | validate_location | — |
| L-crlf-08 | L_crlf_lf | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| S-four-word-09 | S_four_word_sentence | accepted | validate_claims | — |
| S-one-word-04 | S_one_word_substring | accepted | validate_claims | — |
| L-binary-09 | L_binary_file | rejected | validate_location | invalid location: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte |
| L-tab-spaces-05 | L_tab_vs_spaces | accepted | validate_location | — |
| S-four-word-02 | S_four_word_sentence | accepted | validate_claims | — |
| L-int-subclass-06 | L_int_subclass_line_number | accepted | validate_location | — |
| S-one-word-00 | S_one_word_substring | accepted | validate_claims | — |
| L-crlf-02 | L_crlf_lf | rejected | validate_location | code_excerpt does not exactly match the cited on-disk lines |
| L-name-case-04 | L_filename_case | rejected | validate_location | invalid location: [Errno 2] No such file or directory: '/home/ubuntu/rpapercodeaudit/benchmark/fixtures/build/source_repo/R/Sample.txt' |
| L-name-case-07 | L_filename_case | accepted | validate_location | — |
| L-crlf-01 | L_crlf_lf | accepted | validate_location | — |
| L-int-subclass-03 | L_int_subclass_line_number | accepted | validate_location | — |
| L-int-subclass-00 | L_int_subclass_line_number | accepted | validate_location | — |
| S-one-word-09 | S_one_word_substring | accepted | validate_claims | — |
| L-int-subclass-02 | L_int_subclass_line_number | accepted | validate_location | — |
| S-one-word-02 | S_one_word_substring | accepted | validate_claims | — |
