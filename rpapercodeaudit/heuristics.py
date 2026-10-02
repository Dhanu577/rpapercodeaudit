"""No-API heuristic claim extraction."""
from __future__ import annotations
import re
from typing import Any
from .claim_extraction import ValidationResult, validate_claims

_TRIGGER = re.compile(r"\b(we\s+(?:use|used|apply|applied|estimate|estimated|filter|filtered|fit|fitted|compute|computed|calculate|calculated)|(?:default|threshold|cutoff|parameter|formula|equation|significant|p[- ]?value|counts?|genes?|dispersion|normaliz|adjusted|false discovery|fdr|alpha|fold change|filter|fit|estimate|compute))\b", re.I)
_NUMBER = re.compile(r"(?:\b\d+(?:\.\d+)?\b|\b0\.\d+\b|10\s*[-^]\s*[0-9]+|[=<>±]\\?\s*\d)")

def split_sentences(text: str) -> list[str]:
    # Keep punctuation and line breaks so accepted strings remain copied from input.
    return [m.group(0).strip() for m in re.finditer(r"[^.!?\n]*(?:[.!?](?=\s|$)|$)", text) if m.group(0).strip()]

def claim_type(sentence: str) -> str:
    lowered = sentence.lower()
    if any(x in lowered for x in ("filter", "threshold", "cutoff")): return "filtering"
    if any(x in lowered for x in ("p-value", "fdr", "significant", "statistical")): return "statistical_test"
    if any(x in lowered for x in ("formula", "equation", "=", "compute")): return "formula"
    if any(x in lowered for x in ("default", "parameter", "use", "apply")): return "parameters"
    return "other"

def extract_heuristic_items(text: str, *, id_prefix: str = "H") -> list[dict[str, Any]]:
    items = []
    for sentence in split_sentences(text):
        if not (_TRIGGER.search(sentence) or _NUMBER.search(sentence)):
            continue
        items.append({"id": f"{id_prefix}{len(items)+1:04d}", "verbatim_sentence": sentence, "section_or_figure": "unknown", "claim_type": claim_type(sentence), "what_to_look_for": "Check the parameters, defaults, formula, threshold, or statistical rule stated in this sentence."})
    return items

def extract_no_api(text: str) -> ValidationResult:
    return validate_claims(text, extract_heuristic_items(text))

def split_sections(text: str, max_chars: int = 12000) -> list[str]:
    chunks = []
    current = []
    size = 0
    for block in re.split(r"(?m)(?=^\s*(?:[A-Z][A-Za-z0-9 ,:-]{2,80}|\d+(?:\.\d+)*\s+))", text):
        if not block.strip(): continue
        if current and size + len(block) > max_chars:
            chunks.append("".join(current)); current=[]; size=0
        current.append(block); size += len(block)
    if current: chunks.append("".join(current))
    return chunks or [text]
