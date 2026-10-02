"""One-command orchestration for the audit pipeline."""
from __future__ import annotations
import argparse, json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from .claim_extraction import extract_claims
from .code_location import build_index, locate_claims
from .export import export_csv, export_xlsx
from .schema import ClaimRecord
from .verdicts import rule_based_drafts

def run_pipeline(paper_path: str | Path, repo_path: str | Path, commit_hash: str, *, output_dir: str | Path, package: str = "", extraction_mode: str = "no-api", ranking_mode: str = "none", chunk: bool = False) -> dict:
    paper_path, output_dir = Path(paper_path), Path(output_dir); output_dir.mkdir(parents=True, exist_ok=True)
    paper = paper_path.read_text(encoding="utf-8")
    extracted = extract_claims(paper, mode=extraction_mode, chunk=chunk)
    index = build_index(repo_path, commit_hash)
    location_result = locate_claims(index, extracted.accepted, package=package, ranking_mode=ranking_mode)
    drafts = rule_based_drafts(extracted.accepted, location_result.locations, package=package)
    locations_by_claim = {}
    for loc in location_result.locations: locations_by_claim.setdefault(loc.claim_id, []).append(loc)
    records=[]
    timestamp=datetime.now(timezone.utc).isoformat()
    for claim, draft in zip(extracted.accepted, drafts):
        locs=locations_by_claim.get(claim.id, []); loc=locs[0] if locs else None
        records.append(ClaimRecord(id=claim.id, package=package, commit_hash=index.commit_hash, paper_sentence=claim.verbatim_sentence, paper_section=claim.section_or_figure, claim_type=claim.claim_type, expected_implementation=claim.what_to_look_for, code_file=loc.code_file if loc else "", code_lines=loc.code_lines if loc else "", code_excerpt=loc.code_excerpt if loc else "", verdict=draft.verdict, notes=f"{draft.label}: {draft.justification}", llm_model="", prompt_version="", timestamp=timestamp))
    export_csv(records, output_dir / "claims.csv"); export_xlsx(records, output_dir / "claims.xlsx")
    result={"accepted": [asdict(x) for x in extracted.accepted], "rejected": [asdict(x) for x in extracted.rejected], "locations": [x.to_output() for x in location_result.locations], "not_found": location_result.not_found, "invalid": [asdict(x) for x in location_result.invalid], "draft_verdicts": [asdict(x) for x in drafts], "records": [x.to_row() for x in records], "commit_hash": index.commit_hash}
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return result

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("paper", type=Path); p.add_argument("repo", type=Path); p.add_argument("commit_hash"); p.add_argument("--output-dir", type=Path, default=Path("outputs")); p.add_argument("--package", default=""); p.add_argument("--mode", choices=("no-api","demo","llm"), default="no-api"); p.add_argument("--ranking", choices=("none","demo","api"), default="none"); p.add_argument("--chunk", action="store_true"); a=p.parse_args(); print(json.dumps(run_pipeline(a.paper,a.repo,a.commit_hash,output_dir=a.output_dir,package=a.package,extraction_mode=a.mode,ranking_mode=a.ranking,chunk=a.chunk), indent=2, ensure_ascii=False))
if __name__ == "__main__": main()
