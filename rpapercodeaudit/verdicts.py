"""Human-reviewable draft verdicts; never final findings."""
from __future__ import annotations
import json, re
from dataclasses import dataclass, asdict
from typing import Any, Mapping, Iterable
from .claim_extraction import ExtractedClaim
from .code_location import CodeLocation

ALLOWED_VERDICTS = ("consistent", "partial", "inconsistent", "not found", "not verified")
@dataclass(frozen=True, slots=True)
class DraftVerdict:
    claim_id: str
    verdict: str
    label: str
    justification: str
    code_file: str = ""
    code_lines: str = ""
    code_excerpt: str = ""

def _numbers(text: str) -> set[str]: return set(re.findall(r"\b\d+(?:\.\d+)?\b", text))
def _claim_dict(claim: Mapping[str, Any] | ExtractedClaim) -> dict[str, Any]: return asdict(claim) if isinstance(claim, ExtractedClaim) else dict(claim)
def rule_based_drafts(claims: Iterable[Mapping[str, Any] | ExtractedClaim], locations: Iterable[CodeLocation], *, package: str = "") -> list[DraftVerdict]:
    by_claim: dict[str, list[CodeLocation]] = {}
    for loc in locations: by_claim.setdefault(loc.claim_id, []).append(loc)
    output = []
    for claim in claims:
        c = _claim_dict(claim); cid = str(c.get("id", "")); found = by_claim.get(cid, [])
        if not found:
            output.append(DraftVerdict(cid, "not found", "DRAFT - unverified", "No validated keyword location was found.")); continue
        paper_nums = _numbers(str(c.get("verbatim_sentence", "")))
        matching = [loc for loc in found if not paper_nums or paper_nums.intersection(_numbers(loc.code_excerpt))]
        if matching and paper_nums: verdict, why = "consistent", f"Validated excerpt contains claimed numeric value(s): {', '.join(sorted(paper_nums))}."
        elif matching: verdict, why = "partial", "A validated location was found, but no numeric value was available for comparison."
        else: verdict, why = "inconsistent", "Validated locations were found, but the claimed numeric value(s) were not present in the excerpt."
        loc = found[0]
        output.append(DraftVerdict(cid, verdict, "DRAFT - unverified", why, loc.code_file, loc.code_lines, loc.code_excerpt))
    return output

def llm_drafts(claims: Iterable[Mapping[str, Any] | ExtractedClaim], locations: Iterable[CodeLocation], *, client: Any) -> list[DraftVerdict]:
    by_claim: dict[str, list[CodeLocation]] = {}
    for loc in locations: by_claim.setdefault(loc.claim_id, []).append(loc)
    result=[]
    for claim in claims:
        c=_claim_dict(claim); cid=str(c.get("id", "")); locs=by_claim.get(cid, [])
        prompt = json.dumps({"claim": c, "locations": [asdict(x) for x in locs], "allowed_verdicts": ALLOWED_VERDICTS}, ensure_ascii=False)
        data=client.complete_json("Return JSON with verdict and justification. Never guess; use not found when no location.\n"+prompt, purpose="draft-verdict")
        verdict=data.get("verdict", "not verified") if data.get("verdict") in ALLOWED_VERDICTS else "not verified"
        loc=locs[0] if locs else None
        result.append(DraftVerdict(cid, verdict, "DRAFT - unverified", str(data.get("justification", "")), loc.code_file if loc else "", loc.code_lines if loc else "", loc.code_excerpt if loc else ""))
    return result
