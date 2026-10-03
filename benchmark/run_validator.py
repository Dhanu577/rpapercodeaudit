from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rpapercodeaudit.claim_extraction import extract_claims, validate_claims
from rpapercodeaudit.code_location import prepare_repository, validate_location

PINNED_COMMIT = "76c5f8523716804dbe0a9500b4b7e216c6af225c"


def classify_location_error(error: str | None) -> str | None:
    """Summarize the real location validator's error without repeating its checks."""
    if error is None:
        return None
    message = error.casefold()
    if "outside the repository" in message or "no such file or directory" in message or "not a directory" in message:
        return "file"
    if "line range" in message or "outside file with" in message:
        return "line_range"
    if "code_excerpt" in message:
        return "excerpt"
    if "invalid location" in message:
        return "invalid_location"
    return "location"


def evaluate(case: dict[str, Any], paper: str, repo: Path) -> dict[str, Any]:
    claim = {
        "id": case.get("case_id", ""),
        "verbatim_sentence": case["paper_sentence"],
        "section_or_figure": "",
        "claim_type": "other",
        "what_to_look_for": "",
    }
    sentence_result = validate_claims(paper, [claim])
    sentence_match = bool(sentence_result.accepted)

    repo_error: str | None = None
    try:
        _, resolved_commit = prepare_repository(repo, case["commit"])
        repo_commit_valid = resolved_commit == PINNED_COMMIT
        if not repo_commit_valid:
            repo_error = f"resolved commit {resolved_commit} does not match pinned commit {PINNED_COMMIT}"
    except (OSError, RuntimeError, ValueError) as exc:
        repo_commit_valid = False
        repo_error = str(exc)

    location_item = {
        "claim_id": case.get("case_id", ""),
        "package": case.get("repo", ""),
        "commit_hash": case["commit"],
        "code_file": case["file"],
        "start_line": case["line_start"],
        "end_line": case["line_end"],
        "code_excerpt": case["excerpt"],
    }
    location, location_error = validate_location(repo, location_item)
    location_valid = location is not None

    stages = {
        "sentence_match": sentence_match,
        "repo_commit_valid": repo_commit_valid,
        "location": location_valid,
    }
    first_failure = next((name for name, passed in stages.items() if not passed), None)
    return {
        **case,
        "stage_results": stages,
        "final_decision": all(stages.values()),
        "first_failing_stage": first_failure,
        "repo_error": repo_error,
        "location_error": location_error,
        "location_cause": classify_location_error(location_error),
        "mode": "mechanical",
    }


def verify_checksum(cases_path: Path) -> None:
    digest = hashlib.sha256(cases_path.read_bytes()).hexdigest()
    expected = cases_path.with_name("cases.sha256").read_text(encoding="utf-8").split()[0]
    if digest != expected:
        raise SystemExit(f"case checksum mismatch: expected {expected}, got {digest}; refusing to run")


def run_seeded(cases_path: Path, repo: Path, paper_path: Path, output_path: Path, mode: str) -> list[dict[str, Any]]:
    verify_checksum(cases_path)
    cases = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    paper = paper_path.read_text(encoding="utf-8")
    results = [evaluate(case, paper, repo) for case in cases]
    for result in results:
        result["mode"] = mode
    output_path.write_text("".join(json.dumps(result, sort_keys=True, ensure_ascii=False) + "\n" for result in results), encoding="utf-8")
    return results


def run_natural(repo: Path, paper_path: Path, output_dir: Path) -> dict[str, Any]:
    paper = paper_path.read_text(encoding="utf-8")
    result = extract_claims(paper, mode="no-api")
    proposals = []
    for claim in result.accepted:
        proposals.append({"id": claim.id, "verbatim_sentence": claim.verbatim_sentence, "section_or_figure": claim.section_or_figure, "claim_type": claim.claim_type, "what_to_look_for": claim.what_to_look_for})
    (output_dir / "natural_proposals_deterministic.json").write_text(json.dumps({"mode":"deterministic","proposals":proposals,"rejected":[r.__dict__ if hasattr(r,'__dict__') else str(r) for r in result.rejected]}, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = [{"mode":"deterministic","proposals":len(proposals),"accepted":len(result.accepted),"rejected":len(result.rejected),"note":"Claim-level exact sentence validation applied; source-location validation requires explicit locations."}]
    provider = os.environ.get("LLM_PROVIDER", "none").lower()
    if provider not in ("", "none", "no-api", "offline") and os.environ.get("LLM_API_KEY"):
        summary.append({"mode":"llm_assisted","proposals":None,"accepted":None,"rejected":None,"note":"Not run by the seeded benchmark runner; live LLM proposals require an explicit separate run and are not simulated."})
    else:
        summary.append({"mode":"llm_assisted","proposals":None,"accepted":None,"rejected":None,"note":"Skipped: no configured LLM API key; no model output was simulated."})
    with (output_dir / "natural_proposals_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["mode", "proposals", "accepted", "rejected", "note"])
        writer.writeheader(); writer.writerows(summary)
    return {"summary":summary}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=ROOT / "benchmark" / "cases.jsonl")
    parser.add_argument("--repo", type=Path, default=ROOT / "examples" / "deseq2" / "repo")
    parser.add_argument("--paper", type=Path, default=ROOT / "examples" / "deseq2" / "DESeq.txt")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "benchmark")
    parser.add_argument("--mode", choices=("deterministic", "llm_assisted"), default="deterministic")
    parser.add_argument("--natural", action="store_true")
    args = parser.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.natural:
        print(json.dumps(run_natural(args.repo, args.paper, args.output_dir), indent=2)); return
    output = args.output_dir / f"results_{args.mode}.jsonl"
    results = run_seeded(args.cases, args.repo, args.paper, output, args.mode)
    print(json.dumps({"mode": args.mode, "cases": len(results), "accepted": sum(r["final_decision"] for r in results), "rejected": sum(not r["final_decision"] for r in results)}, indent=2))

if __name__ == "__main__": main()
