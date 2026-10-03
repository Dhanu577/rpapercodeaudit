from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

OUT = Path(__file__).resolve().parent
NEAREST = OUT / "nearest_passages.json"
LOCATION = OUT / "location_results_v2.json"
PARTIAL = OUT / "partial_validation.json"
DEST = OUT / "PARTIAL_VALIDATION_v2.md"

# Each sentence-failure proposal receives one primary requested cause label.
# Any secondary observed difference is described in its note.
LABELS: dict[int, tuple[str, str, bool, str]] = {
    2: ("e", "Other — PDF reading order split one sentence around a figure caption", True,
        "Borderline: the model's first clause is present at paper lines 253–254, while the continuation begins at lines 266–269; the figure caption/page material at lines 255–265 interrupts the extracted text. The best-scoring single contiguous window therefore contains only the continuation."),
    4: ("a", "Spacing/whitespace repair", True,
        "Borderline score/window: the complete supporting source region is lines 271–274, but the highest-scoring candidate window is only lines 272–273. The source splits 'standard' as 'stan'/'dard' and fuses 'Methodsfor'."),
    6: ("a", "Spacing/whitespace repair", False, "The source fuses multiple adjacent words, e.g. 'Pvaluesfromthesubsetofgenesthatpassanindependent'."),
    7: ("a", "Spacing/whitespace repair", False, "The source splits line-wrapped words, including 'aver'/'age' and 'mul'/'tiple'."),
    10: ("a", "Spacing/whitespace repair", False, "The source line-wrap splits 'differential' as 'differen'/'tial'."),
    11: ("a", "Spacing/whitespace repair", False, "The matched source sentence is otherwise verbatim but is split at line wraps, including 'num'/'ber'."),
    15: ("a", "Spacing/whitespace repair", False, "The source splits 'empirical' as 'empiri'/'cal'; the proposal's comma after 'and' is also present in the source."),
    16: ("a", "Spacing/whitespace repair", False, "The source splits 'transformation' as 'trans'/'formation'; the fused forms 'theVST' and 'theDESeq2' are also present in the extracted paper."),
    17: ("a", "Spacing/whitespace repair", False, "The source line-wrap splits 'P values' as 'P val'/'ues'."),
    19: ("a", "Spacing/whitespace repair", False, "The source line-wrap splits 'distribution' as 'distribu'/'tion'."),
    22: ("a", "Spacing/whitespace repair", False, "The source line-wrap splits 'sensitivity' between lines as 'sen'/'sitivity' and 'true differences' as 'differ'/'ences'."),
    23: ("a", "Spacing/whitespace repair", False, "The source line-wrap splits 'differences' as 'differ'/'ences'."),
    24: ("a", "Spacing/whitespace repair", False, "The source fuses 'We note' and splits 'normalized' as 'nor'/'malized'."),
    25: ("a", "Spacing/whitespace repair", False, "The source fuses multiple words, e.g. 'chosea', '26RNA-seqsamples', and 'readlength'."),
    27: ("a", "Spacing/whitespace repair", False, "The source fuses 'We estimated' and line-wrap splits 'critical' as 'crit'/'ical'."),
    28: ("a", "Spacing/whitespace repair", False, "The source line-wrap splits 'natural' as 'nat'/'ural'."),
    29: ("a", "Spacing/whitespace repair", False, "The source splits 'considered' as 'consid'/'ered' and fuses 'sj,andareestimated'."),
    30: ("a", "Spacing/whitespace repair", False, "The source line-wrap splits 'addition' as 'addi'/'tion'."),
    31: ("a", "Spacing/whitespace repair", False, "The source line-wrap splits 'estimating' as 'estimat'/'ing'."),
    32: ("b", "Punctuation/quote difference", False,
        "Primary mismatch: the paper uses curly 'gene’s' while the proposal uses straight 'gene's'. The source also line-wraps 'lognormal' as 'log'/'normal'."),
    33: ("e", "Other — equation/OCR layout artifact", True,
        "Borderline: the equation is extracted across lines 1065–1068 with a stray '6)' between the overbar and μ. This makes exact comparison of the formula text uncertain; the surrounding prose is a close match."),
    34: ("a", "Spacing/whitespace repair", False, "The source line-wrap splits 'dispersion' and 'negative' as 'dis'/'persion' and 'nega'/'tive'."),
    39: ("a", "Spacing/whitespace repair", False, "The source line-wrap splits 'subtracting' as 'subtract'/'ing'; the displayed formula is otherwise aligned."),
    40: ("e", "Other — formula content incomplete in extracted text", True,
        "Borderline: the source lines preserve the prose and the beginning of the MAD expression, but the operands/remaining formula are absent or displaced in this text dump. The proposal supplies formula text that cannot be confirmed from the available extraction."),
    41: ("a", "Spacing/whitespace repair", False, "The source line-wrap splits 'underestimate' as 'underes'/'timate' and separates the formula's subscript lines."),
    42: ("a", "Spacing/whitespace repair", False, "The source line-wrap splits 'minimizes' as 'mini'/'mizes'."),
    43: ("a", "Spacing/whitespace repair", False, "The source fuses the preceding period with 'Therefore' and splits 'heuristic' as 'heuris'/'tic'; the remaining prose/formula aligns."),
    44: ("e", "Other — equation/subscript layout artifact", True,
        "Borderline: the surrounding sentence continues at lines 1309–1317, but the subscript i and equation fragments appear as multiple standalone 'i' lines. The best-scoring passage is cut at the formula-layout interruption."),
    49: ("a", "Spacing/whitespace repair", False, "The source has lost spaces throughout the passage, e.g. 'TheWaldtestcomparesthebetaestimate'."),
    51: ("a", "Spacing/whitespace repair", False, "The source line-wrap splits 'independent' as 'indepen'/'dent'."),
    52: ("a", "Spacing/whitespace repair", False, "The source fuses words, including 'meanof' and 'p,theP'."),
    53: ("a", "Spacing/whitespace repair", False, "The source fuses adjacent words throughout, including 'Two-tailedP' and 'Thevalue'."),
    54: ("a", "Spacing/whitespace repair", False, "The source fuses 'theP' and splits 'constructed' as 'con'/'structed'; mathematical spacing also differs."),
    55: ("a", "Spacing/whitespace repair", False, "The source fuses words and line-wrap splits 'normal'/'distribution' fragments."),
    58: ("a", "Spacing/whitespace repair", False, "The source splits 'Second' as 'Sec'/'ond' and fuses 'hypothesis that a' as 'hypothesisthata'."),
    59: ("a", "Spacing/whitespace repair", False, "The source line-wrap splits 'influence' and fuses 're-estimates the'."),
    60: ("a", "Spacing/whitespace repair", False, "The source fuses 'by matching' and splits 'distribution' as 'distribu'/'tion'."),
    62: ("a", "Spacing/whitespace repair", False, "The source splits 'metadata' and the package name 'SummarizedExperiment' across line boundaries."),
    63: ("a", "Spacing/whitespace repair", False, "The source fuses words, including 'isusedtorun'."),
}

BORDERLINE_IDS = {2, 4, 33, 40, 44}


def md_cell(value: str) -> str:
    # JSON quoting preserves embedded newlines/control characters; pipe escaping preserves the table layout.
    rendered = json.dumps(value, ensure_ascii=False).replace("|", r"\|")
    longest = max((len(run) for run in __import__("re").findall(r"`+", rendered)), default=0)
    fence = "`" * (longest + 1)
    return f"{fence}{rendered}{fence}"


def main() -> None:
    nearest = json.loads(NEAREST.read_text(encoding="utf-8"))
    location = json.loads(LOCATION.read_text(encoding="utf-8"))
    partial = json.loads(PARTIAL.read_text(encoding="utf-8"))
    rows = nearest["rows"]
    if len(rows) != 39 or {x["proposal_index"] for x in rows} != set(LABELS):
        raise SystemExit("Failure-analysis rows or manual-label coverage do not match the 39 sentence failures")
    labels_count = Counter(LABELS[x["proposal_index"]][0] for x in rows)

    lines = [
        "# PARTIAL_VALIDATION_v2 — local failure analysis and deterministic locations",
        "",
        "> **PARTIAL ONLY.** The underlying proposal run is incomplete: run1 has proposals only from chunks 2–7; run1 chunks 1, 8, and 9 are missing; run2 did not complete. No model/API calls or extraction were performed for this analysis. Validators and `llm.py` were not modified. No proposal was changed.",
        "",
        "## Frozen run context",
        "",
        "- Model: `gemini-3.8-flash` (recorded response model/version: `gemini-3.8-flash`).",
        "- Settings: OpenAI-compatible Gemini endpoint `https://generativelanguage.googleapis.com/v1beta/openai/chat/completions`; temperature `0`; Bearer key from the secret environment variable (value omitted).",
        "- Run1 completed chunks: **2, 3, 4, 5, 6, 7** (63 saved proposals); missing: **1, 8, 9**. Run2 is incomplete and contributed no completed chunks to these results.",
        "- Paper: `examples/deseq2/DESeq.txt`; repository commit: `76c5f8523716804dbe0a9500b4b7e216c6af225c`.",
        "",
        "## 1. Failure analysis — 39 sentence-stage failures",
        "",
        "### Method",
        "",
        "For each failed model sentence, candidate passages were all contiguous, nonblank line spans from the saved paper text whose whitespace-collapsed character length was 48%–145% of the query length, with a maximum of 22 source lines per span. Similarity is Python `difflib.SequenceMatcher.ratio()` on case-folded character strings with `autojunk=False`; whitespace sequences are collapsed, but spelling, punctuation, symbols, and line-wrap artifacts are otherwise retained. The highest-scoring candidate wins; exact ties prefer closer character length, then earlier source lines. Scores are 0–1. This is a textual nearest-passage measure, not a semantic entailment score.",
        "",
        "Proposal strings below are serialized from the saved JSON without editing; JSON escapes preserve embedded newlines. Each nearest passage is the highest-scoring candidate span. Where PDF reading order or equation layout split support across spans, the case note identifies that limitation.",
        "",
        "### Cause-label counts",
        "",
        "| Label | Count | Interpretation |",
        "|---|---:|---|",
        f"| (a) Spacing/whitespace repair | {labels_count['a']} | Lost, fused, or line-wrapped whitespace in the extracted paper text; proposal restores conventional spacing. |",
        f"| (b) Punctuation/hyphen/quote/ligature | {labels_count['b']} | Punctuation or glyph mismatch is the primary observed cause. |",
        f"| (c) Paraphrase | {labels_count['c']} | Same meaning expressed with different words. |",
        f"| (d) No close match | {labels_count['d']} | No textual support in the nearest paper passage. |",
        f"| (e) Other | {labels_count['e']} | PDF reading order or formula/OCR layout prevents direct sentence-level comparison. |",
        "",
        f"Borderline cases: **{', '.join(map(str, sorted(BORDERLINE_IDS)))}**. The label is uncertain or the best contiguous window omits material because of figure/equation extraction. All other cases have an unambiguous local textual cause under this method.",
        "",
        "### Every sentence failure: model text beside nearest paper passage",
        "",
        "| Proposal index / id | Similarity | Cause | Borderline | Model text (saved proposal) | Nearest paper passage (line span) |",
        "|---:|---:|---|---|---|---|",
    ]
    for row in rows:
        idx = row["proposal_index"]
        code, title, borderline, note = LABELS[idx]
        proposal_id = row["proposal_id"]
        cause = f"({code}) {title}"
        passage_cell = md_cell(f"L{row['paper_lines']}: {row['nearest_passage']}")
        lines.append(
            f"| {idx} / {proposal_id} | {row['score']:.6f} | {cause} | {'YES' if borderline else 'no'} | "
            f"{md_cell(row['model_text'])} | {passage_cell} |"
        )
    lines += ["", "### Borderline-case notes", ""]
    for idx in sorted(BORDERLINE_IDS):
        _, title, _, note = LABELS[idx]
        row = next(x for x in rows if x["proposal_index"] == idx)
        lines.append(f"- **Case {idx} ({row['proposal_id']}, score {row['score']:.6f}; {title}):** {note}")
    lines += [
        "",
        "No sentence failure was classified as paraphrase or unsupported/fabricated based on the nearest text search. This is limited to the saved paper text; formula content omitted by the text extraction is marked as other/borderline, not treated as proof of support.",
        "",
        "## 2. Deterministic code-location stage — 24 sentence-passing proposals",
        "",
        "The earlier **24 location failures were harness gaps, not model failures**: all 24 saved proposals lacked `code_file`, `start_line`, `end_line`, and `code_excerpt`, so directly calling `validate_location` on those pre-location proposals necessarily returned `invalid location: 'code_file'`. Those failures do not indicate that the model selected an incorrect code location.",
        "",
        "The 24 original proposal mappings were left unchanged and passed through the project's normal deterministic locator, as in `pipeline.run_pipeline`: `build_index(repo, commit)` followed by `locate_claims(index, claims, package='DESeq2', ranking_mode='none')` (default window 2, maximum 5 candidates). The batch call mirrors pipeline orchestration; one-item calls were also made solely to attribute results because IDs repeat across chunks. Every returned candidate was then explicitly passed to the real `validate_location`.",
        "",
        "| Sentence-passing proposal count | Accepted proposals (≥1 validated location) | Rejected proposals | Not found | Candidates generated | Candidates accepted by `validate_location` | Candidates rejected by `validate_location` |",
        "|---:|---:|---:|---:|---:|---:|---:|",
        f"| {location['source_proposals_count']} | {location['accepted_proposals']} | {location['rejected_proposals']} | {location['not_found_proposals']} | {location['batch_locator_valid_locations'] + location['batch_locator_invalid_candidates']} | {location['individually_revalidated_candidates_accepted']} | {location['individually_revalidated_candidates_rejected']} |",
        "",
        "Per-proposal result: all 24 proposals generated 5 deterministic candidates each; all **120/120** candidates passed the second, explicit `validate_location` call. There were no not-found claims, locator-invalid entries, or raw location-validator errors in this run.",
        "",
        "No rejection rate or confidence interval is reported. Raw counts only.",
        "",
        "## Reproducibility artifacts",
        "",
        "- Similarity candidates and exact scores: [`nearest_passages.json`](nearest_passages.json).",
        "- Deterministic location results and candidate-level validation records: [`location_results_v2.json`](location_results_v2.json).",
        "- Offline analysis scripts: [`analyze_failures.py`](analyze_failures.py), [`run_locations_v2.py`](run_locations_v2.py).",
        "- The prior report/result files remain unchanged; this file is the v2 interpretation and location-stage correction.",
        "",
    ]
    DEST.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"report": str(DEST), "sentence_failure_labels": dict(labels_count),
                      "borderline_cases": sorted(BORDERLINE_IDS),
                      "location_accepted": location["accepted_proposals"],
                      "location_rejected": location["rejected_proposals"],
                      "candidate_location_accepts": location["individually_revalidated_candidates_accepted"],
                      "report_bytes": DEST.stat().st_size}, indent=2))


if __name__ == "__main__":
    main()
