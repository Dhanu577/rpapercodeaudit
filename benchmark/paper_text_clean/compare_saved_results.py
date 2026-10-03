from __future__ import annotations

import json
import sys
from dataclasses import asdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark.analyze_natural_v3_1 import (  # existing report-only heuristics
    SHORT_SENTENCE_TOKEN_LIMIT,
    is_reference_like,
)
from rpapercodeaudit.claim_extraction import (
    extract_claims,
    normalize_whitespace,
    validate_claims,
)

CLEAN_DIR = ROOT / "benchmark" / "paper_text_clean"
OLD_PAPER = ROOT / "examples" / "deseq2" / "DESeq.txt"
SAVED_PROPOSALS = ROOT / "benchmark" / "llm_proposals_v1" / "run1" / "proposals_unmodified.json"
PILOT_CASES = ROOT / "benchmark" / "cases.jsonl"
BASELINE = {"total": 319, "short_sentence": 193, "reference_like": 114}


def nearest_passage(sentence: str, paper: str) -> tuple[float, str]:
    target = normalize_whitespace(sentence)
    target_words = target.split()
    paper_words = normalize_whitespace(paper).split()
    width = len(target_words)
    if not target or not paper_words:
        return 0.0, ""
    if width >= len(paper_words):
        candidate = " ".join(paper_words)
        return SequenceMatcher(None, target, candidate).ratio(), candidate
    best_start = 0
    best_score = -1.0
    for start in range(len(paper_words) - width + 1):
        candidate = " ".join(paper_words[start : start + width])
        score = SequenceMatcher(None, target, candidate).ratio()
        if score > best_score:
            best_start, best_score = start, score
            if score == 1.0:
                break
    context_start = max(0, best_start - 6)
    context_end = min(len(paper_words), best_start + width + 6)
    return best_score, " ".join(paper_words[context_start:context_end])


def one_item_result(paper: str, item: dict[str, Any]) -> tuple[bool, str | None]:
    result = validate_claims(paper, [item])
    if result.accepted:
        return True, None
    return False, result.rejected[0].reason


def quote(text: str) -> str:
    return "\n".join("> " + line for line in text.splitlines()) if text else "> *(empty)*"


def report() -> str:
    clean_paper = (CLEAN_DIR / "paper_clean.txt").read_text(encoding="utf-8")
    old_paper = OLD_PAPER.read_text(encoding="utf-8")
    proposals: list[dict[str, Any]] = json.loads(SAVED_PROPOSALS.read_text(encoding="utf-8"))
    if len(proposals) != 63:
        raise ValueError(f"Expected 63 saved run1 proposals, found {len(proposals)}")

    outcomes: list[dict[str, Any]] = []
    for index, item in enumerate(proposals, 1):
        old_pass, old_error = one_item_result(old_paper, item)
        clean_pass, clean_error = one_item_result(clean_paper, item)
        outcomes.append({
            "index": index,
            "item": item,
            "old_pass": old_pass,
            "old_error": old_error,
            "clean_pass": clean_pass,
            "clean_error": clean_error,
        })

    old_failures = [row for row in outcomes if not row["old_pass"]]
    old_passes = [row for row in outcomes if row["old_pass"]]
    if (len(old_failures), len(old_passes)) != (39, 24):
        raise ValueError(
            "The unchanged old paper text did not reproduce the recorded 39/24 split: "
            f"failures={len(old_failures)}, passes={len(old_passes)}"
        )
    failed_old_now_pass = [row for row in old_failures if row["clean_pass"]]
    failed_old_still_fail = [row for row in old_failures if not row["clean_pass"]]
    passed_old_now_fail = [row for row in old_passes if not row["clean_pass"]]

    pilot = [
        json.loads(line)
        for line in PILOT_CASES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    pilot = [row for row in pilot if row.get("tier") == "A" and row.get("expected_valid") is True]
    if len(pilot) != 24:
        raise ValueError(f"Expected 24 original valid Tier-A pilot cases, found {len(pilot)}")
    pilot_results = []
    for row in pilot:
        sentence = row["paper_sentence"]
        item = {
            "id": row["case_id"],
            "verbatim_sentence": sentence,
            "section_or_figure": str(row.get("source_record_id", "")),
            "claim_type": "other",
            "what_to_look_for": "",
        }
        passed, error = one_item_result(clean_paper, item)
        pilot_results.append({"case": row, "sentence": sentence, "passed": passed, "error": error})
    pilot_passes = [row for row in pilot_results if row["passed"]]
    pilot_failures = [row for row in pilot_results if not row["passed"]]

    deterministic = extract_claims(clean_paper, mode="no-api", chunk=False)
    deterministic_items = [asdict(claim) for claim in deterministic.accepted]
    deterministic_items.extend(rejected.item for rejected in deterministic.rejected)
    short_count = sum(
        len(normalize_whitespace(item.get("verbatim_sentence", "")).split()) < SHORT_SENTENCE_TOKEN_LIMIT
        for item in deterministic_items
    )
    reference_count = sum(is_reference_like(item.get("verbatim_sentence", "")) for item in deterministic_items)
    overlap_count = sum(
        len(normalize_whitespace(item.get("verbatim_sentence", "")).split()) < SHORT_SENTENCE_TOKEN_LIMIT
        and is_reference_like(item.get("verbatim_sentence", ""))
        for item in deterministic_items
    )

    lines = [
        "# Clean paper text comparison — PARTIAL Gemini experiment",
        "",
        "## Scope and status",
        "",
        "All checks in this report are offline. No Gemini or other model/API call was made. Sentence validation used the unchanged project `validate_claims()` function; the deterministic run used the unchanged `extract_claims(..., mode=\"no-api\")` path. Saved proposals and pilot sentences were not edited.",
        "",
        "**The Gemini experiment remains PARTIAL:** run1 completed only chunks 2–7 (63 saved proposals); chunks 1, 8, and 9 are missing. Run2 is incomplete and produced no successful chunk. Model: `gemini-3.8-flash`; response/resolved version: `gemini-3.8-flash`; temperature `0`; OpenAI-compatible base URL `https://generativelanguage.googleapis.com/v1beta/openai/chat/completions`; Bearer authorization sourced from the secret environment variable. No final rejection rate or confidence interval is calculated.",
        "",
        f"Clean text SHA-256: `{(CLEAN_DIR / 'paper_clean.sha256').read_text(encoding='utf-8').split()[0]}`. The pre-comparison freeze tag is `clean-text-frozen`.",
        "",
        "## 3a. The 39 sentences that failed on the old text",
        "",
        f"Of the 39 original sentence-stage failures, **{len(failed_old_now_pass)} now pass** and **{len(failed_old_still_fail)} still fail** against the frozen clean text.",
        "",
    ]
    if failed_old_still_fail:
        lines.append("Each remaining failure is listed below with the exact validator error and its highest-similarity clean-text passage. Similarity is `difflib.SequenceMatcher.ratio()` after whitespace collapse only; it is report-layer context, not a validation rule.")
        lines.append("")
        for row in failed_old_still_fail:
            score, passage = nearest_passage(row["item"]["verbatim_sentence"], clean_paper)
            lines.extend([
                f"### Proposal {row['index']} — `{row['item'].get('id', '')}`",
                "",
                "**Original proposal text:**",
                quote(row["item"]["verbatim_sentence"]),
                "",
                f"**Raw validator error:** `{row['clean_error']}`",
                "",
                f"**Nearest clean passage (similarity {score:.4f}):**",
                quote(passage),
                "",
            ])
    else:
        lines.append("No remaining failures; therefore there are no raw errors or nearest-passage failure entries for this subset.")
        lines.append("")

    lines.extend([
        "## 3b. The 24 sentences that passed on the old text",
        "",
        f"Of the 24 old-text sentence passes, **{len(old_passes) - len(passed_old_now_fail)} still pass** and **{len(passed_old_now_fail)} now fail** against the clean text.",
        "",
    ])
    if passed_old_now_fail:
        lines.append("For each newly failing case, the original proposal and the nearest old/clean passages are shown side by side in sequence. The validator error is unmodified.")
        lines.append("")
        for row in passed_old_now_fail:
            old_score, old_passage = nearest_passage(row["item"]["verbatim_sentence"], old_paper)
            clean_score, clean_passage = nearest_passage(row["item"]["verbatim_sentence"], clean_paper)
            lines.extend([
                f"### Proposal {row['index']} — `{row['item'].get('id', '')}`",
                "",
                "**Original proposal text:**",
                quote(row["item"]["verbatim_sentence"]),
                "",
                f"**Raw validator error:** `{row['clean_error']}`",
                "",
                f"**Nearest old-text passage (similarity {old_score:.4f}):**",
                quote(old_passage),
                "",
                f"**Nearest clean-text passage (similarity {clean_score:.4f}):**",
                quote(clean_passage),
                "",
            ])
    else:
        lines.append("No old-text sentence pass became a clean-text failure.")
        lines.append("")

    lines.extend([
        "## 3c. Original Tier-A pilot positives",
        "",
        f"The 24 original positive cases were selected unchanged from frozen `benchmark/cases.jsonl` using `tier == \"A\"` and `expected_valid == true`. **{len(pilot_passes)} pass** and **{len(pilot_failures)} fail** sentence validation against the clean text.",
        "",
    ])
    if pilot_failures:
        for row in pilot_failures:
            case = row["case"]
            lines.extend([
                f"- **{case['case_id']}** (source `{case.get('source_record_id', '')}`): {row['error']}",
                "  - Original pilot sentence:",
                *["    > " + text for text in row["sentence"].splitlines()],
            ])
        lines.append("")
    else:
        lines.append("No pilot records failed; the records and their sentence text remain unchanged.")
        lines.append("")

    deterministic_total = len(deterministic_items)
    lines.extend([
        "## 3d. Unchanged deterministic extractor on clean text",
        "",
        "Report-only flags use the existing definitions: `short_sentence` means fewer than 5 whitespace-delimited tokens; `reference_like` uses the existing report-only citation/reference heuristic. Neither flag changes acceptance.",
        "",
        "| Text/input | Total proposals | Accepted by no-API path | Rejected by no-API path | `short_sentence` | `reference_like` | Both flags |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| Clean publisher text (this run) | {deterministic_total} | {len(deterministic.accepted)} | {len(deterministic.rejected)} | {short_count} | {reference_count} | {overlap_count} |",
        f"| Old-text baseline (saved, unchanged) | {BASELINE['total']} | not recomputed here | not recomputed here | {BASELINE['short_sentence']} | {BASELINE['reference_like']} | not available in the specified baseline |",
        "",
        "## 3e. All 63 saved Gemini proposals",
        "",
        "| Paper text | Total saved proposals | Pass `validate_claims()` | Fail `validate_claims()` |",
        "|---|---:|---:|---:|",
        f"| Old `examples/deseq2/DESeq.txt` | {len(outcomes)} | {sum(row['old_pass'] for row in outcomes)} | {sum(not row['old_pass'] for row in outcomes)} |",
        f"| Clean `paper_clean.txt` | {len(outcomes)} | {sum(row['clean_pass'] for row in outcomes)} | {sum(not row['clean_pass'] for row in outcomes)} |",
        "",
        "These are raw counts for the available 63 proposals only. They are not complete-run estimates; chunks 1, 8, and 9 and the second run remain unavailable.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    report_path = CLEAN_DIR / "CLEAN_TEXT_REPORT.md"
    report_path.write_text(report(), encoding="utf-8", newline="\n")
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
