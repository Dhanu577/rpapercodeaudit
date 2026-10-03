from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rpapercodeaudit.code_location import build_index, locate_claims, validate_location

OUT = Path(__file__).resolve().parent
PARTIAL = OUT / "partial_validation.json"
PROPOSALS_PATH = OUT / "run1" / "proposals_unmodified.json"
REPO = ROOT / "examples" / "deseq2" / "repo"
COMMIT = "76c5f8523716804dbe0a9500b4b7e216c6af225c"
PACKAGE = "DESeq2"


def main() -> None:
    partial = json.loads(PARTIAL.read_text(encoding="utf-8"))
    rows = [x for x in partial["rejections"] if x["first_failing_stage"] == "location"]
    if len(rows) != 24:
        raise SystemExit(f"Expected exactly 24 proposals that passed sentence validation; found {len(rows)}")
    proposals = [x["proposal"] for x in rows]
    source_hash_before = hashlib.sha256(PROPOSALS_PATH.read_bytes()).hexdigest()

    # These are the same deterministic location-stage calls used by run_pipeline:
    # build_index(repo, commit), then locate_claims(..., package=..., ranking_mode='none').
    index = build_index(REPO, COMMIT)
    batch = locate_claims(index, proposals, package=PACKAGE, ranking_mode="none")

    per_proposal: list[dict[str, Any]] = []
    validated_candidate_count = 0
    rejected_candidate_count = 0
    raw_errors: list[dict[str, Any]] = []
    locator_not_found = 0
    locator_invalid_count = 0
    for row in rows:
        proposal = row["proposal"]
        # Run the same deterministic locator independently for attributable results
        # because claim ids repeat across chunks in this saved proposal set.
        result = locate_claims(index, [proposal], package=PACKAGE, ranking_mode="none")
        candidates = []
        proposal_errors = []
        for loc in result.locations:
            item = asdict(loc)
            verified, error = validate_location(index.repo_path, item)
            if verified is not None:
                validated_candidate_count += 1
                candidates.append({
                    "code_file": verified.code_file,
                    "start_line": verified.start_line,
                    "end_line": verified.end_line,
                    "code_lines": verified.code_lines,
                    "status": verified.status,
                })
            else:
                rejected_candidate_count += 1
                failure = {"proposal_index": row["proposal_index"], "proposal_id": proposal.get("id", ""), "raw_validator_error": error}
                proposal_errors.append(failure)
                raw_errors.append(failure)
        for invalid in result.invalid:
            locator_invalid_count += 1
            verified, error = validate_location(index.repo_path, invalid.item)
            raw_error = error or invalid.reason
            rejected_candidate_count += 1
            failure = {
                "proposal_index": row["proposal_index"],
                "proposal_id": proposal.get("id", ""),
                "raw_validator_error": raw_error,
                "locator_reason": invalid.reason,
            }
            proposal_errors.append(failure)
            raw_errors.append(failure)
        not_found_rows = result.not_found
        if not_found_rows:
            locator_not_found += 1
        accepted = bool(candidates)
        per_proposal.append({
            "proposal_index": row["proposal_index"],
            "proposal_id": proposal.get("id", ""),
            "model_text": proposal.get("verbatim_sentence", ""),
            "accepted_by_deterministic_locator_and_location_validator": accepted,
            "validated_candidate_count": len(candidates),
            "not_found": bool(not_found_rows),
            "candidate_locations": candidates,
            "raw_errors": proposal_errors,
        })

    batch_validated_count = len(batch.locations)
    batch_invalid_count = len(batch.invalid)
    per_item_validated_count = validated_candidate_count
    per_item_invalid_count = rejected_candidate_count
    counts = Counter("accepted" if x["accepted_by_deterministic_locator_and_location_validator"] else "rejected" for x in per_proposal)
    source_hash_after = hashlib.sha256(PROPOSALS_PATH.read_bytes()).hexdigest()
    output = {
        "scope": "PARTIAL",
        "method": "Project deterministic pipeline location stage: build_index(repo, commit) then locate_claims(index, proposals, package='DESeq2', ranking_mode='none', default window=2 and max_candidates=5); every returned CodeLocation was then passed through real validate_location. A batch call matches pipeline orchestration; one-item calls are used only to associate results with repeated proposal ids.",
        "api_calls": 0,
        "source_proposals_count": len(proposals),
        "source_proposals_sha256_before": source_hash_before,
        "source_proposals_sha256_after": source_hash_after,
        "source_proposals_unchanged": source_hash_before == source_hash_after,
        "repo_path": str(index.repo_path),
        "commit_hash": index.commit_hash,
        "package": PACKAGE,
        "ranking_mode": "none",
        "window": 2,
        "max_candidates": 5,
        "accepted_proposals": counts["accepted"],
        "rejected_proposals": counts["rejected"],
        "not_found_proposals": locator_not_found,
        "batch_locator_valid_locations": batch_validated_count,
        "batch_locator_invalid_candidates": batch_invalid_count,
        "individually_revalidated_candidates_accepted": per_item_validated_count,
        "individually_revalidated_candidates_rejected": per_item_invalid_count,
        "locator_invalid_entries": locator_invalid_count,
        "raw_errors": raw_errors,
        "proposals": per_proposal,
    }
    target = OUT / "location_results_v2.json"
    target.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: output[k] for k in (
        "source_proposals_count", "accepted_proposals", "rejected_proposals", "not_found_proposals",
        "batch_locator_valid_locations", "batch_locator_invalid_candidates",
        "individually_revalidated_candidates_accepted", "individually_revalidated_candidates_rejected",
        "locator_invalid_entries", "source_proposals_unchanged"
    )}, indent=2))


if __name__ == "__main__":
    main()
