# v2 boundary investigation for validator spec v3

This is a report of `benchmark/results_v2.jsonl` and the frozen v2 inputs only. It does not judge whether an observed behavior is correct.

## CRLF file versus LF/CRLF excerpt

The on-disk fixture is `R/crlf.txt`, whose bytes use CRLF (`crlf alpha\r\ncrlf beta\r\n`). `validate_location` reads it through `Path.read_text(encoding="utf-8")`; Python's universal-newline text mode presents those lines to the comparison as LF. The expected excerpt is the varying side:

| Cases | Excerpt supplied | Outcome | Explanation |
|---|---|---|---|
| `L-crlf-00`, `02`, `04`, `06`, `08` | `crlf alpha\r\n` | Rejected (5/5) | The excerpt retains CRLF, while the text read from the CRLF file is normalized to LF before exact comparison. |
| `L-crlf-01`, `03`, `05`, `07`, `09` | `crlf alpha\n` | Accepted (5/5) | The supplied excerpt matches the LF text produced by reading the CRLF file. |

The repository file itself is unchanged across the cases. The differing outcome is due to the excerpt newline representation relative to text-mode file reading.

## Tab versus spaces

The on-disk `R/tab_spaces.txt` line is `left\tright\n` and remains constant. The excerpt is the varying side:

| Cases | Excerpt supplied | Outcome | Explanation |
|---|---|---|---|
| `L-tab-spaces-00`, `02`, `04`, `06`, `08` | `left    right\n` (four spaces) | Rejected (5/5) | Four spaces are not the literal tab in the file line. |
| `L-tab-spaces-01`, `03`, `05`, `07`, `09` | `left\tright\n` | Accepted (5/5) | The excerpt contains the same tab character as the file. |

The outcome follows exact excerpt equality; no tabs-to-spaces expansion is observed.

## File-name case on Linux

Only `R/sample.txt` (lowercase `s`) exists in the synthetic repository. On the Linux filesystem used for v2:

| Cases | Path supplied | Outcome | Explanation |
|---|---|---|---|
| `L-name-case-00`, `02`, `04`, `06`, `08` | `R/Sample.txt` | Rejected (5/5) | The case-sensitive filesystem reports that this differently cased path does not exist. |
| `L-name-case-01`, `03`, `05`, `07`, `09` | `R/sample.txt` | Accepted (5/5) | The path names the existing file and the excerpt matches. |

The difference is the path spelling/filesystem lookup; the excerpt is identical. This observation is specific to the Linux filesystem used in this run.

## NFC versus NFD sentence text

The paper contains `The café item is stored in composed form.` with `é` encoded as NFC (U+00E9). The generated claim alternates between NFC and NFD (`e` followed by U+0301):

| Cases | Claim encoding | Outcome | Explanation |
|---|---|---|---|
| `S-unicode-00`, `02`, `04`, `06`, `08` | NFD | Rejected (5/5) | The claim's code-point sequence is not the same substring as the NFC paper text. |
| `S-unicode-01`, `03`, `05`, `07`, `09` | NFC | Accepted (5/5) | The claim's code points match the paper text. |

Whitespace normalization does not perform Unicode canonical normalization. Only the claim text varies; the paper side remains NFC.

## Files outside indexed directories

All ten cases, `L-outside-index-00` through `L-outside-index-09`, cite an exact one-line excerpt from a separate `docs/outside-scope-NN.txt` file. All ten were accepted. The cited file type in every case is a UTF-8 text file with the `.txt` suffix. `INDEX_DIRS` governs index/search traversal; `validate_location` validates repository containment and exact line text but does not require a cited path to be beneath one of those directories.
