# Paused Gemini proposal experiment — partial results

**PARTIAL.** The retry loop is paused and no model/API request is active. Raw attempt bodies are preserved under `run1/raw_responses/` and `run2/raw_responses/`; key values were checked and scrubbed. Only the 63 saved run1 proposals from chunks 2–7 have since been passed through the real validators; missing run1 chunks and run2 were not validated.

- Pause request received: 2026-10-03 16:51:18 +05:30.
- Interrupt delivered: 2026-10-03 16:52:01 +05:30.
- The background runner had already advanced into run2 before the interrupt reached the terminal. It was stopped during run2 chunk 7; this is reported rather than hidden.

## PARTIAL validation of the saved run1 proposals

- Model: `gemini-3.8-flash`; response model/version: `gemini-3.8-flash`.
- Settings: `https://generativelanguage.googleapis.com/v1beta/openai/chat/completions`, temperature `0`, Bearer key sourced from the secret environment variable (value omitted).
- Run1 completed chunks: **2, 3, 4, 5, 6, 7**. Run1 chunks **1, 8, 9 are missing**; run2 **did not complete**.
- Of the 63 saved proposals, **0 accepted**, **63 rejected**: sentence first failures **39**, commit **0**, location **24**. Report-only flags on fully accepted proposals: short sentence **0**, reference-like **0**. Raw validator errors and every rejected item are listed in [PARTIAL_VALIDATION.md](PARTIAL_VALIDATION.md). No final rejection rate or confidence interval is calculated.

## Run 1 chunk status

| Chunk | HTTP attempts | State | Proposals saved |
|---:|---|---|---:|
| 1 | 503, 503, 503, 503 | gave_up_after_retries | 0 |
| 2 | 200 | completed | 8 |
| 3 | 503, 503, 200 | completed | 8 |
| 4 | 503, 200 | completed | 11 |
| 5 | 503, 200 | completed | 9 |
| 6 | 503, 200 | completed | 12 |
| 7 | 503, 200 | completed | 15 |
| 8 | 429, 429, 429, 429 | gave_up_after_retries | 0 |
| 9 | 429, 429, 429, 429 | gave_up_after_retries | 0 |

**Run 1 total:** 63 proposals saved from successful chunks 2–7; 3 chunks gave up (1, 8, 9); 0 malformed responses; 15 retry events.

## Run 2 status at interruption

| Chunk | HTTP attempts | State | Proposals saved |
|---:|---|---|---:|
| 1 | 429, 429, 429, 429 | gave_up_after_retries | 0 |
| 2 | 429, 429, 429, 429 | gave_up_after_retries | 0 |
| 3 | 429, 429, 429, 429 | gave_up_after_retries | 0 |
| 4 | 429, 429, 429, 429 | gave_up_after_retries | 0 |
| 5 | 429, 429, 429, 429 | gave_up_after_retries | 0 |
| 6 | 429, 429, 429, 429 | gave_up_after_retries | 0 |
| 7 | 429, 429 | interrupted_before_retry_completion | 0 |
| 8 | — | not_started | 0 |
| 9 | — | not_started | 0 |

Run2 chunks 1–6 each received four HTTP 429 responses and exhausted the retry budget. Chunk 7 received two HTTP 429 responses; retry attempt 3 was logged with a 30-second backoff, but no third request was made before interruption. Chunks 8–9 were not started. **Run2 yielded no successful chunk response and no proposals.** Its partial proposal file is an explicit empty array; all 26 attempted raw response bodies and call records remain preserved.

## Retry log so far

Each row is one retry/backoff event. The exact JSONL records are preserved in [retry_log_so_far.jsonl](retry_log_so_far.jsonl), and in each run-specific `retry_log.jsonl`.

| Run | Chunk | Retry attempt | Previous status | Backoff | Request for retry made? |
|---|---:|---:|---:|---:|---|
| run1 | 1 | 2 | 503 | 10s | yes |
| run1 | 1 | 3 | 503 | 30s | yes |
| run1 | 1 | 4 | 503 | 90s | yes |
| run1 | 3 | 2 | 503 | 10s | yes |
| run1 | 3 | 3 | 503 | 30s | yes |
| run1 | 4 | 2 | 503 | 10s | yes |
| run1 | 5 | 2 | 503 | 10s | yes |
| run1 | 6 | 2 | 503 | 10s | yes |
| run1 | 7 | 2 | 503 | 10s | yes |
| run1 | 8 | 2 | 429 | 10s | yes |
| run1 | 8 | 3 | 429 | 30s | yes |
| run1 | 8 | 4 | 429 | 90s | yes |
| run1 | 9 | 2 | 429 | 10s | yes |
| run1 | 9 | 3 | 429 | 30s | yes |
| run1 | 9 | 4 | 429 | 90s | yes |
| run2 | 1 | 2 | 429 | 10s | yes |
| run2 | 1 | 3 | 429 | 30s | yes |
| run2 | 1 | 4 | 429 | 90s | yes |
| run2 | 2 | 2 | 429 | 10s | yes |
| run2 | 2 | 3 | 429 | 30s | yes |
| run2 | 2 | 4 | 429 | 90s | yes |
| run2 | 3 | 2 | 429 | 10s | yes |
| run2 | 3 | 3 | 429 | 30s | yes |
| run2 | 3 | 4 | 429 | 90s | yes |
| run2 | 4 | 2 | 429 | 10s | yes |
| run2 | 4 | 3 | 429 | 30s | yes |
| run2 | 4 | 4 | 429 | 90s | yes |
| run2 | 5 | 2 | 429 | 10s | yes |
| run2 | 5 | 3 | 429 | 30s | yes |
| run2 | 5 | 4 | 429 | 90s | yes |
| run2 | 6 | 2 | 429 | 10s | yes |
| run2 | 6 | 3 | 429 | 30s | yes |
| run2 | 6 | 4 | 429 | 90s | yes |
| run2 | 7 | 2 | 429 | 10s | yes |
| run2 | 7 | 3 | 429 | 30s | no — interrupted during backoff |

Run1 retry events: 15 (503 on chunks 1, 3–7; 429 on chunks 8–9). Run2 retry events: 20 (429 on chunks 1–7; the final logged chunk-7 retry had not yet been sent).

## Saved artifacts

- Run1 unmodified proposals: `run1/proposals_unmodified.json` (63 items).
- Run1 calls/retries/raw bodies: `run1/calls.jsonl`, `run1/retry_log.jsonl`, `run1/raw_responses/`.
- Run2 partial proposal list: `run2/proposals_unmodified_partial.json` (empty because no chunk completed).
- Run2 partial manifest/calls/retries/raw bodies: `run2/partial_manifest.json`, `run2/calls.jsonl`, `run2/retry_log.jsonl`, `run2/raw_responses/`.
- No run2 retry was resumed, no further API calls were made, and no commit or PR was created while the run is incomplete.
