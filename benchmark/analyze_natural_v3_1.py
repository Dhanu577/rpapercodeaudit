from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rpapercodeaudit.claim_extraction import normalize_whitespace, validate_claims

SHORT_SENTENCE_TOKEN_LIMIT = 5
REFERENCE_PATTERNS = (
    re.compile(r"^\s*(?:\[\s*)?\d+(?:[.,:/\u2013\u2014-]\d+)*(?:\s*\])?[.;:]?\s*$"),
    re.compile(r"\[\s*\d+(?:\s*[,;\u2013\u2014-]\s*\d+)*\s*\]"),
    re.compile(r"\b(?:doi|pmid|isbn)\s*[:#]?\s*\S+", re.IGNORECASE),
    re.compile(r"\bhttps?://\S+|\bwww\.\S+", re.IGNORECASE),
    re.compile(r"\(\s*[A-Z][\w'\u2019.-]*(?:\s+et\s+al\.?)?,?\s*(?:18|19|20)\d{2}[a-z]?\s*\)", re.IGNORECASE),
    re.compile(r"^\s*(?:\[\d{1,4}\]|\d{1,3}[.)])\s+\S"),
    re.compile(r"^\s*(?:references?|bibliography)\b", re.IGNORECASE),
)


def is_reference_like(sentence: str) -> bool:
    normalized = normalize_whitespace(sentence)
    return any(pattern.search(normalized) for pattern in REFERENCE_PATTERNS)


def analyze(input_path: Path, paper_path: Path, csv_path: Path, summary_path: Path) -> dict[str, Any]:
    saved = json.loads(input_path.read_text(encoding="utf-8"))
    proposals = saved["proposals"]
    paper_text = paper_path.read_text(encoding="utf-8")
    result = validate_claims(paper_text, proposals)
    accepted_ids = {claim.id for claim in result.accepted}
    rejected_by_id = {rejected.item.get("id"): rejected.reason for rejected in result.rejected}

    rows: list[dict[str, Any]] = []
    short_count = reference_count = both_count = 0
    for proposal in proposals:
        sentence = proposal["verbatim_sentence"]
        normalized = normalize_whitespace(sentence)
        token_count = len(normalized.split())
        short_sentence = token_count < SHORT_SENTENCE_TOKEN_LIMIT
        reference_like = is_reference_like(sentence)
        short_count += short_sentence
        reference_count += reference_like
        both_count += short_sentence and reference_like
        proposal_id = proposal["id"]
        rows.append({
            "id": proposal_id,
            "verbatim_sentence": sentence,
            "normalized_token_count": token_count,
            "short_sentence": short_sentence,
            "reference_like": reference_like,
            "accepted_by_validate_claims": proposal_id in accepted_ids,
            "validator_error": rejected_by_id.get(proposal_id),
        })

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["id"] , lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "source": str(input_path),
        "proposal_count": len(proposals),
        "accepted": len(result.accepted),
        "rejected": len(result.rejected),
        "short_sentence_token_limit_exclusive": SHORT_SENTENCE_TOKEN_LIMIT,
        "short_sentence_count": short_count,
        "reference_like_count": reference_count,
        "both_flags_count": both_count,
        "neither_flag_count": len(proposals) - short_count - reference_count + both_count,
        "flags_are_report_only": True,
        "reference_like_heuristic": "numeric-only values/ranges, numbered reference prefixes, numeric bracket citations, author-year citations, DOI/URL/PMID/ISBN markers, and explicit reference/bibliography headings",
        "csv": str(csv_path),
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Report-only flags for the saved deterministic claim proposals.")
    parser.add_argument("--input", type=Path, default=ROOT / "benchmark" / "natural_proposals_deterministic.json")
    parser.add_argument("--paper", type=Path, default=ROOT / "examples" / "deseq2" / "DESeq.txt")
    parser.add_argument("--csv", type=Path, default=ROOT / "benchmark" / "natural_proposals_v3_1_flags.csv")
    parser.add_argument("--summary", type=Path, default=ROOT / "benchmark" / "natural_proposals_v3_1_summary.json")
    args = parser.parse_args()
    print(json.dumps(analyze(args.input, args.paper, args.csv, args.summary), indent=2))


if __name__ == "__main__":
    main()
