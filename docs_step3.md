# Step 3: code location

The locator indexes `R/`, `src/`, `man/`, `vignettes/`, and `tests/` using
`pathlib` and Python file reads. It does not require ripgrep, grep, bash, or
other Linux-only tools.

## Inputs

- local cloned Git repository;
- commit hash to audit;
- Step 2 JSON output containing an `accepted` list (or a JSON list of claims).

By default, the tool detaches the clone at the requested commit without using a
force/reset operation. Use `--no-checkout` to require that `HEAD` already
matches. The resolved full commit hash is included in every location and
`not_found` row.

## Windows Command Prompt

From Command Prompt, use these commands with no shell-specific variable prefix:

```text
cd C:\path\to\RPaperCodeAudit
py -m pip install -r requirements.txt
py -m rpapercodeaudit.code_location C:\path\to\DESeq2 0123456789abcdef0123456789abcdef01234567 C:\path\to\accepted_claims.json --package DESeq2 --output C:\path\to\locations.json
```

To require an already-pinned checkout:

```text
py -m rpapercodeaudit.code_location C:\path\to\DESeq2 0123456789abcdef0123456789abcdef01234567 C:\path\to\accepted_claims.json --package DESeq2 --no-checkout --output C:\path\to\locations.json
```

To exercise the saved ranking response without an API key or credits:

```text
py -m rpapercodeaudit.code_location C:\path\to\DESeq2 0123456789abcdef0123456789abcdef01234567 C:\path\to\accepted_claims.json --package DESeq2 --ranking demo --output C:\path\to\locations.json
```

The output has separate `locations`, `not_found`, and `invalid` lists. Every
location is re-read from disk at its cited line range; altered excerpts and
wrong ranges are discarded into `invalid` with a reason.

## R parsing limitation

R function names and defaults are parsed with a lightweight regex when building
the index. If R is installed, a future enhancement can use R's parser; this
step does not execute package code. The regex may miss unusual, nested, or
multi-module definitions. C/C++ indexing is text/keyword based and does not
provide a full language AST.
