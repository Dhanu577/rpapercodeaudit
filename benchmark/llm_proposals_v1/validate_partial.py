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

from benchmark.analyze_natural_v3_1 import is_reference_like
from rpapercodeaudit.claim_extraction import normalize_whitespace, validate_claims
from rpapercodeaudit.code_location import prepare_repository, validate_location

OUT = Path(__file__).resolve().parent
RUN1_PROPOSALS = OUT / "run1" / "proposals_unmodified.json"
RUN1_MANIFEST = OUT / "run1" / "manifest.json"
PAPER_PATH = ROOT / "examples" / "deseq2" / "DESeq.txt"


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    paper = PAPER_PATH.read_text(encoding="utf-8")
    manifest = json.loads(RUN1_MANIFEST.read_text(encoding="utf-8"))
    proposals = json.loads(RUN1_PROPOSALS.read_text(encoding="utf-8"))
    if len(proposals) != 63:
        raise SystemExit(f"Expected exactly the 63 saved run1 proposals; found {len(proposals)}")

    input_sha_before = hashlib.sha256(RUN1_PROPOSALS.read_bytes()).hexdigest()
    repo_path = ROOT / manifest["repo_path"]
    commit_hash = manifest["commit_hash"]
    errors: list[dict[str, Any]] = []
    sentence_pass: list[tuple[int, Any]] = []
    first_counts: Counter[str] = Counter()

    # Each original object is passed as-is; no fields, ids, text, or excerpts are added or rewritten.
    for index, proposal in enumerate(proposals, start=1):
        result = validate_claims(paper, [proposal])
        if result.rejected:
            rejected = result.rejected[0]
            text = proposal.get("verbatim_sentence", "") if isinstance(proposal, dict) else str(proposal)
            errors.append({
                "proposal_index": index,
                "proposal": proposal,
                "text": text,
                "first_failing_stage": "sentence",
                "raw_validator_error": rejected.reason,
            })
            first_counts["sentence"] += 1
        else:
            sentence_pass.append((index, proposal))

    repo_state: dict[str, Any]
    try:
        prepared_repo, resolved_commit = prepare_repository(repo_path, commit_hash)
        repo_state = {
            "ok": True,
            "requested_commit": commit_hash,
            "resolved_commit": resolved_commit,
            "repo_path": str(prepared_repo),
            "error": None,
        }
    except (OSError, RuntimeError, ValueError) as exc:
        repo_state = {
            "ok": False,
            "requested_commit": commit_hash,
            "resolved_commit": None,
            "repo_path": str(repo_path),
            "error": str(exc),
        }

    accepted: list[dict[str, Any]] = []
    for index, proposal in sentence_pass:
        if not repo_state["ok"]:
            text = proposal.get("verbatim_sentence", "") if isinstance(proposal, dict) else str(proposal)
            errors.append({
                "proposal_index": index,
                "proposal": proposal,
                "text": text,
                "first_failing_stage": "commit",
                "raw_validator_error": repo_state["error"],
            })
            first_counts["commit"] += 1
            continue
        location, error = validate_location(repo_path, proposal)
        if location is None:
            text = proposal.get("verbatim_sentence", "") if isinstance(proposal, dict) else str(proposal)
            errors.append({
                "proposal_index": index,
                "proposal": proposal,
                "text": text,
                "first_failing_stage": "location",
                "raw_validator_error": error,
            })
            first_counts["location"] += 1
        else:
            accepted.append({"proposal_index": index, "proposal": proposal, "location": asdict(location)})

    counts = {
        "result_scope": "PARTIAL",
        "proposals_checked": len(proposals),
        "accepted": len(accepted),
        "rejected": len(errors),
        "rejections_by_first_failing_stage": {stage: first_counts.get(stage, 0) for stage in ("sentence", "commit", "location")},
        "malformed_model_responses_in_saved_chunks": manifest.get("malformed_responses", []),
        "short_sentence_flags_on_accepted_lt_5_whitespace_tokens": sum(
            len(normalize_whitespace(str((row["proposal"].get("verbatim_sentence", "") if isinstance(row["proposal"], dict) else row["proposal"]))).split()) < 5
            for row in accepted
        ),
        "reference_like_flags_on_accepted": sum(
            is_reference_like(str(row["proposal"].get("verbatim_sentence", "") if isinstance(row["proposal"], dict) else row["proposal"]))
            for row in accepted
        ),
        "repo_preparation": repo_state,
        "input_proposals_sha256_before": input_sha_before,
        "input_proposals_sha256_after": hashlib.sha256(RUN1_PROPOSALS.read_bytes()).hexdigest(),
        "input_proposals_unchanged": input_sha_before == hashlib.sha256(RUN1_PROPOSALS.read_bytes()).hexdigest(),
        "model": manifest.get("requested_model"),
        "resolved_version": manifest.get("resolved_version_from_step0_response_model"),
        "settings": {
            "base_url": manifest.get("base_url"),
            "temperature": manifest.get("temperature"),
            "auth_scheme": manifest.get("auth_scheme"),
            "paper_path": manifest.get("paper_path"),
            "commit_hash": commit_hash,
            "completed_chunks": [2, 3, 4, 5, 6, 7],
            "missing_run1_chunks": [1, 8, 9],
            "run2_state": "incomplete; no successful chunks; no proposals",
        },
        "rejections": errors,
        "accepted_proposals": accepted,
    }
    write_json(OUT / "partial_validation.json", counts)

    lines = [
        "# PARTIAL — Run1 validator results (chunks 2–7 only)",
        "",
        "This report covers exactly the 63 saved, unmodified model proposals from run1 chunks 2–7. It is not a full-paper result: run1 chunks 1, 8, and 9 are missing, and run2 did not complete. No rejection rate or confidence interval is calculated.",
        "",
        "## Model and settings",
        "",
        f"- Model: `{counts['model']}`; response model/version recorded at model choice: `{counts['resolved_version']}`.",
        f"- Endpoint: `{counts['settings']['base_url']}`.",
        f"- Temperature: `{counts['settings']['temperature']}`.",
        "- Authorization: Bearer token sourced from the secret environment variable; key value omitted.",
        f"- Paper: `{counts['settings']['paper_path']}`; repository commit: `{commit_hash}`.",
        "- Run1 completed chunks: **2, 3, 4, 5, 6, 7** (63 proposals). Missing run1 chunks: **1, 8, 9**.",
        "- Run2: **incomplete**; no successful chunks and no proposals; no further model calls were made after interruption.",
        "",
        "## Raw counts (PARTIAL only)",
        "",
        "| Proposals checked | Accepted | Rejected | First failure: sentence | commit | location | Short flags on accepted (<5 tokens) | Reference-like flags on accepted |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
        f"| {counts['proposals_checked']} | {counts['accepted']} | {counts['rejected']} | {first_counts.get('sentence', 0)} | {first_counts.get('commit', 0)} | {first_counts.get('location', 0)} | {counts['short_sentence_flags_on_accepted_lt_5_whitespace_tokens']} | {counts['reference_like_flags_on_accepted']} |",
        "",
        "`validate_claims`, `prepare_repository`, and `validate_location` were used directly. Each raw proposal object was passed without adding or changing fields. Report-only flags do not affect acceptance. The input proposal file SHA-256 is unchanged: `" + str(counts['input_proposals_unchanged']) + ".",
        "",
        "## Every rejected proposal and raw validator error",
        "",
    ]
    if not errors:
        lines.extend(["No rejected proposals.", ""])
    for row in errors:
        lines.extend([
            f"### Proposal {row['proposal_index']} — first failure: {row['first_failing_stage']}",
            "",
            "**Model text:**",
            "",
            "> " + str(row["text"]).replace("\n", " "),
            "",
            "**Raw validator error:**",
            "",
            "```text",
            str(row["raw_validator_error"]),
            "```",
            "",
            "**Unmodified proposal:**",
            "",
            "```json",
            json.dumps(row["proposal"], ensure_ascii=False, indent=2),
            "```",
            "",
        ])
    (OUT / "PARTIAL_VALIDATION.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({k: counts[k] for k in (
        "result_scope", "proposals_checked", "accepted", "rejected",
        "rejections_by_first_failing_stage", "short_sentence_flags_on_accepted_lt_5_whitespace_tokens",
        "reference_like_flags_on_accepted", "input_proposals_unchanged"
    )}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
