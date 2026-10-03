# Reproduce the citation-integrity benchmark

All commands below run from the RPaperCodeAudit repository root. The benchmark treats DESeq2 as static text and never executes R, C++, package installation scripts, or repository code.

## Inputs

- DESeq2 URL: `https://github.com/thelovelab/DESeq2`
- Pinned commit: `76c5f8523716804dbe0a9500b4b7e216c6af225c`
- Paper: `examples/deseq2/DESeq.txt`
- Evidence workbook: `examples/deseq2/final/deseq2_final_table.xlsx`

## Install

```bash
python3 -m pip install -r requirements.txt
```

## Re-run

```bash
python3 benchmark/generate_cases.py
python3 benchmark/run_validator.py --mode deterministic
python3 benchmark/run_validator.py --mode llm_assisted
python3 benchmark/run_validator.py --natural
python3 benchmark/compute_metrics.py
python3 -m pytest -q benchmark/tests
python3 -W error -m unittest discover -s tests -v
```

The generated case file is checksummed before validation. The runner refuses to run if `benchmark/cases.sha256` does not match `benchmark/cases.jsonl`. The seeded `llm_assisted` mode does not call an API; it verifies that the same frozen mechanical cases produce the same result. Natural LLM proposals are skipped unless an API provider and key are explicitly configured; no model output is simulated.

## Windows Command Prompt

```text
py -m pip install -r requirements.txt
py benchmark\generate_cases.py
py benchmark\run_validator.py --mode deterministic
py benchmark\run_validator.py --mode llm_assisted
py benchmark\run_validator.py --natural
py benchmark\compute_metrics.py
py -m pytest -q benchmark\tests
py -W error -m unittest discover -s tests -v
```
