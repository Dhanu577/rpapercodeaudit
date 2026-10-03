from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PAPER = ROOT / "examples" / "deseq2" / "DESeq.txt"
RESULTS = OUT / "partial_validation.json"


def collapse_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def candidate_windows(lines: list[str], query_length: int) -> list[tuple[int, int, str]]:
    """Return contiguous, nonblank line spans around the query's character length."""
    low = max(25, int(query_length * 0.48))
    high = max(low + 1, int(query_length * 1.45))
    found: list[tuple[int, int, str]] = []
    for start, line in enumerate(lines):
        if not line.strip():
            continue
        parts: list[str] = []
        length = 0
        for end in range(start, min(len(lines), start + 22)):
            current = lines[end].strip()
            if not current:
                break
            parts.append(current)
            candidate = collapse_whitespace(" ".join(parts))
            length = len(candidate)
            if length > high:
                break
            if length >= low:
                found.append((start + 1, end + 1, candidate))
    return found


def best_passage(query: str, lines: list[str]) -> dict[str, Any]:
    q = collapse_whitespace(query).casefold()
    candidates = candidate_windows(lines, len(q))
    best: tuple[float, int, int, str] | None = None
    for start, end, passage in candidates:
        score = SequenceMatcher(None, q, passage.casefold(), autojunk=False).ratio()
        row = (score, start, end, passage)
        if best is None or score > best[0] or (score == best[0] and (abs(len(passage) - len(q)), start) < (abs(len(best[3]) - len(q)), best[1])):
            best = row
    if best is None:
        return {"score": 0.0, "paper_lines": None, "nearest_passage": ""}
    return {"score": round(best[0], 6), "paper_lines": f"{best[1]}-{best[2]}", "nearest_passage": best[3]}


def main() -> None:
    paper_lines = PAPER.read_text(encoding="utf-8").splitlines()
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    rows = []
    for item in results["rejections"]:
        if item["first_failing_stage"] != "sentence":
            continue
        query = item["text"]
        rows.append({
            "proposal_index": item["proposal_index"],
            "proposal_id": item["proposal"].get("id", ""),
            "model_text": query,
            **best_passage(query, paper_lines),
        })
    target = OUT / "nearest_passages.json"
    target.write_text(json.dumps({
        "method": "For each sentence-stage failure, enumerate all contiguous nonblank paper line spans whose whitespace-collapsed character length is 48%-145% of the query, up to 22 lines. Score each query/passage pair by Python difflib.SequenceMatcher.ratio() on case-folded character strings with autojunk=False. Highest score wins; ties choose closer character length, then earlier lines. Scores are 0-1. No text normalization beyond collapsing whitespace and case-folding is applied before scoring.",
        "candidate_count_rule": "contiguous source line spans; blank lines stop a span",
        "rows": rows,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "output": str(target), "mean_score": round(sum(r["score"] for r in rows)/len(rows), 4) if rows else None,
                      "min_score": min((r["score"] for r in rows), default=None), "max_score": max((r["score"] for r in rows), default=None)}, indent=2))


if __name__ == "__main__":
    main()
