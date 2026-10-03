# Regression report: v1/v2 on the v3.1 validator

Comparisons use the original committed result files and the new, separately named rerun outputs. A v1 row is listed if its final decision **or any stage result** changed. A v2 row is listed when the real validator's `observed` acceptance outcome changed. No case was reclassified.

- V1 cases compared: 422; changed outcomes/stages: **0**.
- V2 cases compared: 520; changed outcomes: **65**.

## V1 case changes

No v1 final decision or stage result changed.

## V2 case changes

| Case | Group | Mutation | Class | Old observed | New observed | Old raw error | New raw error |
|---|---|---|---|---|---|---|---|
| C_HEAD-00-checkout-false | commit | C_HEAD | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_HEAD-00-checkout-true | commit | C_HEAD | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_HEAD-01-checkout-false | commit | C_HEAD | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_HEAD-01-checkout-true | commit | C_HEAD | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_HEAD-02-checkout-false | commit | C_HEAD | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_HEAD-02-checkout-true | commit | C_HEAD | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_HEAD-03-checkout-false | commit | C_HEAD | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_HEAD-03-checkout-true | commit | C_HEAD | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_HEAD-04-checkout-false | commit | C_HEAD | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_HEAD-04-checkout-true | commit | C_HEAD | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_HEAD_parent-00-checkout-true | commit | C_HEAD_parent | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_HEAD_parent-01-checkout-true | commit | C_HEAD_parent | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_HEAD_parent-02-checkout-true | commit | C_HEAD_parent | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_HEAD_parent-03-checkout-true | commit | C_HEAD_parent | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_HEAD_parent-04-checkout-true | commit | C_HEAD_parent | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_branch_name-00-checkout-false | commit | C_branch_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_branch_name-00-checkout-true | commit | C_branch_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_branch_name-01-checkout-false | commit | C_branch_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_branch_name-01-checkout-true | commit | C_branch_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_branch_name-02-checkout-false | commit | C_branch_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_branch_name-02-checkout-true | commit | C_branch_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_branch_name-03-checkout-false | commit | C_branch_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_branch_name-03-checkout-true | commit | C_branch_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_branch_name-04-checkout-false | commit | C_branch_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_branch_name-04-checkout-true | commit | C_branch_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_short_hash-00-checkout-false | commit | C_short_hash | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_short_hash-00-checkout-true | commit | C_short_hash | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_short_hash-01-checkout-false | commit | C_short_hash | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_short_hash-01-checkout-true | commit | C_short_hash | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_short_hash-02-checkout-false | commit | C_short_hash | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_short_hash-02-checkout-true | commit | C_short_hash | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_short_hash-03-checkout-false | commit | C_short_hash | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_short_hash-03-checkout-true | commit | C_short_hash | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_short_hash-04-checkout-false | commit | C_short_hash | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_short_hash-04-checkout-true | commit | C_short_hash | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_tag_name-00-checkout-false | commit | C_tag_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_tag_name-00-checkout-true | commit | C_tag_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_tag_name-01-checkout-false | commit | C_tag_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_tag_name-01-checkout-true | commit | C_tag_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_tag_name-02-checkout-false | commit | C_tag_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_tag_name-02-checkout-true | commit | C_tag_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_tag_name-03-checkout-false | commit | C_tag_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_tag_name-03-checkout-true | commit | C_tag_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_tag_name-04-checkout-false | commit | C_tag_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| C_tag_name-04-checkout-true | commit | C_tag_name | boundary | True | False | — | commit_hash must be exactly 40 hexadecimal characters |
| L-line-type-00 | location | L_line_number_coercion | boundary | True | False | — | invalid location: start_line must be an integer (bool, str, float, and None are not accepted) |
| L-line-type-01 | location | L_line_number_coercion | boundary | True | False | — | invalid location: start_line must be an integer (bool, str, float, and None are not accepted) |
| L-line-type-02 | location | L_line_number_coercion | boundary | True | False | — | invalid location: start_line must be an integer (bool, str, float, and None are not accepted) |
| L-line-type-03 | location | L_line_number_coercion | boundary | True | False | — | invalid location: start_line must be an integer (bool, str, float, and None are not accepted) |
| L-line-type-04 | location | L_line_number_coercion | boundary | True | False | — | invalid location: start_line must be an integer (bool, str, float, and None are not accepted) |
| L-line-type-05 | location | L_line_number_coercion | boundary | True | False | — | invalid location: start_line must be an integer (bool, str, float, and None are not accepted) |
| L-line-type-06 | location | L_line_number_coercion | boundary | True | False | — | invalid location: start_line must be an integer (bool, str, float, and None are not accepted) |
| L-line-type-07 | location | L_line_number_coercion | boundary | True | False | — | invalid location: start_line must be an integer (bool, str, float, and None are not accepted) |
| L-line-type-08 | location | L_line_number_coercion | boundary | True | False | — | invalid location: start_line must be an integer (bool, str, float, and None are not accepted) |
| L-line-type-09 | location | L_line_number_coercion | boundary | True | False | — | invalid location: start_line must be an integer (bool, str, float, and None are not accepted) |
| S-empty-00 | sentence | S_empty_or_whitespace | boundary | True | False | — | verbatim_sentence must be non-empty after whitespace normalization |
| S-empty-01 | sentence | S_empty_or_whitespace | boundary | True | False | — | verbatim_sentence must be non-empty after whitespace normalization |
| S-empty-02 | sentence | S_empty_or_whitespace | boundary | True | False | — | verbatim_sentence must be non-empty after whitespace normalization |
| S-empty-03 | sentence | S_empty_or_whitespace | boundary | True | False | — | verbatim_sentence must be non-empty after whitespace normalization |
| S-empty-04 | sentence | S_empty_or_whitespace | boundary | True | False | — | verbatim_sentence must be non-empty after whitespace normalization |
| S-empty-05 | sentence | S_empty_or_whitespace | boundary | True | False | — | verbatim_sentence must be non-empty after whitespace normalization |
| S-empty-06 | sentence | S_empty_or_whitespace | boundary | True | False | — | verbatim_sentence must be non-empty after whitespace normalization |
| S-empty-07 | sentence | S_empty_or_whitespace | boundary | True | False | — | verbatim_sentence must be non-empty after whitespace normalization |
| S-empty-08 | sentence | S_empty_or_whitespace | boundary | True | False | — | verbatim_sentence must be non-empty after whitespace normalization |
| S-empty-09 | sentence | S_empty_or_whitespace | boundary | True | False | — | verbatim_sentence must be non-empty after whitespace normalization |

All rows above retain their original case labels. Full new result records are in `results_v1_on_v3validator.jsonl` and `results_v2_on_v3validator.jsonl`.
