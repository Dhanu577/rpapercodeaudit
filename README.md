# RPaperCodeAudit

RPaperCodeAudit is a human-in-the-loop annotation helper for auditing paper/code consistency in R/Bioconductor packages. Automatic outputs are **drafts only**; the Streamlit reviewer must tick **Checked by me** before a result is treated as human-reviewed. The tool never executes package R or C++ code.

## Current status

Milestones 1–6 are implemented locally: schema/export, exact claim validation, no-API heuristic extraction, commit-pinned code location, optional provider-neutral LLM mode, draft verdicts, review UI, and one-command pipeline. The DESeq2 case study and external-table evaluation are recorded honestly as unavailable when their inputs are not present. A GitHub URL was not supplied: the requested placeholder `[PASTE REPO URL]` cannot be used as a remote.

## Setup

Python 3.11 or newer is supported. Install the minimal dependencies:

```bash
python -m pip install -r requirements.txt
```

For Windows Command Prompt, use:

```text
py -m pip install -r requirements.txt
```

The default mode requires no API key. Copy `.env.example` only if you intend to configure an optional LLM provider; never commit `.env`.

## Modes

The default claim extraction mode is deterministic and offline. It selects sentences with checkable signals such as numeric values, defaults, thresholds, formulas, or implementation verbs such as “use”, “filter”, “fit”, “estimate”, and “compute”. Every selected sentence still passes the unchanged exact-substring validator: whitespace is normalized, but case, punctuation, wording, and numbers are not changed. Rejected claims are retained with reasons.

```bash
python -m rpapercodeaudit.claim_extraction paper.txt --mode no-api
```

Use the saved response for a no-credit demo:

```bash
python -m rpapercodeaudit.claim_extraction demo/example_paper.txt --mode demo
```

For optional LLM extraction, configure `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL` in the process environment. Supported provider styles are `anthropic` and any OpenAI-compatible endpoint such as Groq. The `--chunk` flag splits long text by section-sized chunks, merges claims, removes exact duplicates, and assigns unique IDs.

```bash
python -m rpapercodeaudit.claim_extraction paper.txt --mode llm --chunk
```

No API key is read in no-API or demo mode. LLM prompts, responses, provider, model, and timestamps are logged to JSONL when an LLM call occurs; API keys are excluded. Responses are cached.

## Code location and draft verdicts

The locator indexes `R/`, `src/`, `man/`, `vignettes/`, and `tests/` with `pathlib` and Python reads. It verifies or checks out the requested Git commit and records the resolved full hash on every result row. Keyword search is the default and requires no API. `--ranking demo` uses the saved response. `--ranking api` enables optional LLM ranking through the generic environment configuration.

```bash
python -m rpapercodeaudit.code_location /path/to/DESeq2 FULL_COMMIT_HASH accepted_claims.json --package DESeq2 --ranking none --output locations.json
```

On Windows Command Prompt, use `py`, Windows paths, and no `VAR=value` prefix or backslash line continuation:

```text
py -m rpapercodeaudit.code_location C:\work\DESeq2 FULL_COMMIT_HASH C:\work\accepted_claims.json --package DESeq2 --ranking none --output C:\work\locations.json
```

Every candidate excerpt is re-read from disk at its cited line range and must match exactly. Failed validations are listed under `invalid`; claims with no location are listed under `not_found`.

Rule-based draft verdicts compare located excerpts with claimed numeric values and produce `consistent`, `partial`, `inconsistent`, or `not found`. The label is always `DRAFT - unverified`. The optional LLM verdict path is also constrained to the allowed verdict values and cannot remove that draft label.

## One-command pipeline

The pipeline runs paper → claims → locations → rule-based draft verdicts → `results.json`, `claims.csv`, and `claims.xlsx`:

```bash
python -m rpapercodeaudit.pipeline paper.txt /path/to/DESeq2 FULL_COMMIT_HASH --package DESeq2 --output-dir outputs
```

Windows Command Prompt:

```text
py -m rpapercodeaudit.pipeline C:\work\paper.txt C:\work\DESeq2 FULL_COMMIT_HASH --package DESeq2 --output-dir C:\work\outputs
```

The XLSX has a frozen header, wrapped text, a verdict dropdown, and a Summary sheet with `COUNTIF` formulas.

## Human review UI

Run:

```bash
streamlit run app.py
```

Windows Command Prompt:

```text
py -m streamlit run app.py
```

Load `outputs/results.json`. The paper sentence appears beside the validated code excerpt. Reviewers can select a verdict, edit the issue category list in `config.json`, add notes, tick `Checked by me`, save progress, and export CSV/XLSX. Unticked rows remain visibly marked as drafts.

## DESeq2 case study

The requested case-study commit is `76c5f8523716804dbe0a9500b4b7e216c6af225c` from `https://github.com/thelovelab/DESeq2`. The current workspace contains neither the requested `DESeq.txt` nor `deseq2_pilot_combined_table.xlsx`, so the case study cannot honestly be run against the attached inputs in this run. See `examples/deseq2/evaluation.md` for the explicit unavailable-input record. No package code was executed.

## Tests

```bash
python -W error -m unittest discover -s tests -v
```

Windows Command Prompt:

```text
py -W error -m unittest discover -s tests -v
```

Known limitations are documented in `ARCHITECTURE.md`: function-level search misses multi-module logic, R/C++ coverage is partial, regex R parsing is lightweight, and heuristic extraction misses claims. This project makes no detection-accuracy or benchmarking claim.
