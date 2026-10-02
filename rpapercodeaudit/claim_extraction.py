"""Claim extraction with strict paper-quote validation and no-API default."""
from __future__ import annotations
import argparse, json, re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

PROMPT_VERSION = "claim-extraction-v2"

@dataclass(frozen=True, slots=True)
class ExtractedClaim:
    id: str
    verbatim_sentence: str
    section_or_figure: str
    claim_type: str
    what_to_look_for: str

@dataclass(frozen=True, slots=True)
class RejectedClaim:
    item: dict[str, Any]
    reason: str

@dataclass(frozen=True, slots=True)
class ValidationResult:
    accepted: list[ExtractedClaim]
    rejected: list[RejectedClaim]

def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def _claim_from_item(item: Mapping[str, Any], index: int) -> ExtractedClaim:
    required = ("verbatim_sentence", "section_or_figure", "claim_type", "what_to_look_for")
    missing = [field for field in required if not isinstance(item.get(field), str)]
    if missing: raise ValueError(f"missing or non-string fields: {', '.join(missing)}")
    return ExtractedClaim(str(item.get("id") or f"C{index:04d}"), item["verbatim_sentence"], item["section_or_figure"], item["claim_type"], item["what_to_look_for"])

def validate_claims(paper_text: str, items: Iterable[Mapping[str, Any]]) -> ValidationResult:
    """Accept only exact sentence substrings after whitespace normalization.

    No fuzzy matching, case folding, punctuation normalization, stemming, or
    edit-distance matching is performed.
    """
    normalized_paper = normalize_whitespace(paper_text)
    accepted, rejected = [], []
    for index, raw in enumerate(items, 1):
        item = dict(raw) if isinstance(raw, Mapping) else {"value": raw}
        try: claim = _claim_from_item(item, index)
        except ValueError as exc:
            rejected.append(RejectedClaim(item, f"invalid claim shape: {exc}")); continue
        if normalize_whitespace(claim.verbatim_sentence) not in normalized_paper:
            rejected.append(RejectedClaim(asdict(claim), "verbatim_sentence is not an exact substring after whitespace normalization"))
        else: accepted.append(claim)
    return ValidationResult(accepted, rejected)

def build_prompt(paper_text: str) -> str:
    return f'''Extract checkable implementation claims. Return JSON only: {{"claims": [{{"id":"C0001","verbatim_sentence":"...","section_or_figure":"...","claim_type":"parameters|defaults|formula|algorithm|input_output|statistical_test|filtering|other","what_to_look_for":"..."}}]}}. Copy verbatim_sentence exactly from the supplied text; never paraphrase or invent.\n\nPAPER TEXT:\n{paper_text}'''

def load_demo_response(path: str | Path | None = None) -> dict[str, Any]:
    return json.loads((Path(path) if path else Path(__file__).parent.parent / "demo" / "example_response.json").read_text(encoding="utf-8"))

def _llm_items(text: str, *, client: Any) -> list[dict[str, Any]]:
    result = client.complete_json(build_prompt(text), purpose="claim-extraction")
    if not isinstance(result.get("claims"), list): raise ValueError("LLM response must contain a claims list")
    return [dict(item) for item in result["claims"]]

def extract_claims(paper_text: str, *, mode: str = "no-api", chunk: bool = False, demo_response: str | Path | None = None, client: Any = None) -> ValidationResult:
    """Extract claims in no-API, saved-demo, or optional configured LLM mode."""
    from .heuristics import extract_heuristic_items, split_sections
    if mode == "no-api":
        return validate_claims(paper_text, extract_heuristic_items(paper_text))
    if mode == "demo":
        return validate_claims(paper_text, load_demo_response(demo_response).get("claims", []))
    if mode != "llm": raise ValueError(f"unknown extraction mode: {mode}")
    if client is None:
        from .llm import LLMClient
        client = LLMClient()
    chunks = split_sections(paper_text) if chunk else [paper_text]
    raw: list[dict[str, Any]] = []
    for chunk_index, part in enumerate(chunks, 1):
        for item in _llm_items(part, client=client):
            item["id"] = f"C{chunk_index:02d}-{item.get('id') or len(raw)+1:>4}"
            raw.append(item)
    # Deduplicate exact normalized quotes while preserving first occurrence.
    seen: set[str] = set(); unique = []
    for item in raw:
        key = normalize_whitespace(str(item.get("verbatim_sentence", "")))
        if key and key not in seen: seen.add(key); unique.append(item)
    return validate_claims(paper_text, unique)

def _print_result(result: ValidationResult) -> None:
    print(json.dumps({"accepted": [asdict(x) for x in result.accepted], "rejected": [asdict(x) for x in result.rejected]}, indent=2, ensure_ascii=False))

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("paper", type=Path)
    p.add_argument("--mode", choices=("no-api", "demo", "llm"), default="no-api")
    p.add_argument("--demo", action="store_true", help="Alias for --mode demo")
    p.add_argument("--demo-response", type=Path)
    p.add_argument("--chunk", action="store_true", help="Split paper by section/chunk before LLM extraction")
    args = p.parse_args()
    mode = "demo" if args.demo else args.mode
    result = extract_claims(args.paper.read_text(encoding="utf-8"), mode=mode, chunk=args.chunk, demo_response=args.demo_response)
    _print_result(result)

if __name__ == "__main__": main()
