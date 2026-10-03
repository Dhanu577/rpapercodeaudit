# DESeq2 citation-integrity benchmark

This benchmark evaluates the mechanical citation-integrity boundary of RPaperCodeAudit. It does not claim to assess semantic relevance, implementation correctness, or whether a paper claim is scientifically true.

## Frozen inputs

- Audited repository: DESeq2 at `76c5f8523716804dbe0a9500b4b7e216c6af225c`
- Repository URL: `https://github.com/thelovelab/DESeq2`
- Paper: `examples/deseq2/DESeq.txt`
- Evidence records: `examples/deseq2/final/deseq2_final_table.xlsx`
- Seed: `42`

`cases.jsonl` is frozen by `cases.sha256`. The runner refuses to run if the checksum differs.

The case file and checksum were generated and written **before** the seeded validator runs. The validator did not modify the frozen cases.

## Validator stages

`run_validator.py` delegates its checks to the project validators: `validate_claims()` checks the paper sentence, `prepare_repository()` resolves and checks out the requested commit, and `validate_location()` verifies the file, line range, and exact excerpt as one `location` stage. The benchmark's repository/commit stage passes only when the resolved commit is the pinned commit. The wrapper records the real location validator's error and, where its message permits, a cause category; it does not recreate the validators' checks. Results record the first failing stage in sentence, repository/commit, location order.

Tier A contains one valid case and mechanically invalid mutations: altered sentence, nonexistent sentence, wrong commit, wrong file/excerpt pairing, and invalid line ranges. Tier B contains authentic but semantically irrelevant, misleading, contradictory, or compound evidence. Tier B is expected to be mechanically accepted and is reported as the intended scope boundary, not as a validator failure.

## Reproduce

```bash
python3 benchmark/generate_cases.py
python3 benchmark/run_validator.py --mode deterministic
python3 benchmark/run_validator.py --mode llm_assisted
python3 benchmark/compute_metrics.py
pytest -q benchmark/tests
```

The seeded deterministic and LLM-assisted modes use the same frozen cases and mechanical wrapper. No API key is needed for the seeded comparison. Natural-proposal LLM mode is skipped when no key is configured; model output is never simulated.

DESeq2 is treated as static text. The benchmark never runs R, C++, package installation scripts, or repository code.
