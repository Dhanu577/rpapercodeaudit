# RPaperCodeAudit architecture

## Flow

`paper.txt` → claim extraction → exact quote validation → repository commit pinning and pure-Python index → keyword candidates → optional ranking → exact on-disk excerpt validation → rule-based draft verdict → Streamlit human review → CSV/XLSX.

## Safety boundaries

- Default mode is no-API heuristic/keyword mode.
- LLM calls are optional, provider-neutral, cached, and logged without API keys.
- Verbatim paper claims are accepted only after whitespace-only normalization and exact substring matching.
- Code excerpts are re-read from disk and must exactly equal the cited line range.
- The requested Git commit is recorded on each location and export row.
- Automatic verdicts are drafts. The UI requires `Checked by me` before a human-reviewed result is considered reviewed.
- The package's R/C++ code is never executed.

## Known limitations

Function-level search misses multi-module logic. R/C++ coverage is partial and text-based. Regex R parsing can miss unusual syntax. Heuristic extraction misses claims. No accuracy or benchmarking claim is made.
