# Validator benchmark v3 — stopped at the natural-proposal gate

## Status and scope

The v3 specification, validator changes, tests, static case generator, runner, 580 cases, and checksum were frozen and pushed in commit `f112715` on branch `validator-spec-v3`, then tagged `benchmark-cases-v3-frozen`. The runner and input checksum are present, but **the v3 cases were not executed**.

The stop condition in Step 3 triggered: the required `MIN_WORDS = 5` rule rejects 193 of the 319 saved deterministic natural proposals. It also rejects one of the 24 original valid Tier-A pilot records. The threshold was not lowered and no labels were changed. See `min_words_impact.md` for the full rejected-proposal list and the pilot case detail.

## Frozen case inventory (input labels only; not observed results)

| Class | Cases |
|---|---:|
| `must_accept` | 125 |
| `must_reject` | 395 |
| `boundary` | 60 |
| **Total** | **580** |

There are 58 mutation types, with at least 10 cases per type (seed 42). Group counts are 160 sentence, 150 commit, and 270 location cases. These are counts of frozen inputs, not pass/fail results.

## Post-freeze checks completed before stopping

- Existing project tests: **15 passed** (the original 12 plus three new rule-focused tests).
- V3 static case-label/checksum tests: **2 passed** after correcting the Unicode special-case in the test.
- Original pilot positives: **23/24 accepted**. `row-6-A0` is rejected only at `sentence_match` because its normalized text has four tokens; repository and location stages passed.
- Natural deterministic proposals: **126 accepted, 193 rejected**. LLM-assisted proposals were skipped because no API key was configured; no model output was simulated.

## Four rule changes

| Gap | New contract | Observed check available before stop |
|---|---|---|
| Commit references | Only 40 ASCII hex characters; uppercase normalizes to lowercase; symbolic and short refs reject | Unit test covers uppercase full SHA and malformed/symbolic forms; full v3 commit cases not run |
| Claim sentences | Exact normalized substring with at least five whitespace-delimited tokens | Unit test covers empty, whitespace-only, four-word reject, exact-five accept; natural/pilot impacts are listed above |
| Location line numbers | Python `int` except `bool`; no coercion from `str`, `float`, or `None` | Unit test covers these types and a Python `int` subclass; v3 boundary cases not run |
| Spec references | Changed validator docstrings point to `VALIDATOR_SPEC.md` | Source review only |

## Not run because the stop condition fired

No `results_v3.jsonl`, v3 acceptance/rejection rates, Wilson intervals, or observed boundary table were produced. The v1 422-case and v2 520-case full regression runs were not started, so no regression-change list or v3 benchmark bug count is available. These omissions are deliberate; no outcomes are inferred or fabricated.

## Limitations

The existing project tests are written by the validator's own team. The frozen cases use 10 examples per mutation type. The observed v2 filesystem behavior documented in `investigation_v3.md` is specific to Linux. The v3 benchmark and full regressions remain unrun due to the explicit natural-proposal impact gate.
