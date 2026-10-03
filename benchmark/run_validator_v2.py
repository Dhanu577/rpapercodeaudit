from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rpapercodeaudit.claim_extraction import validate_claims
from rpapercodeaudit.code_location import prepare_repository, validate_location


class ChecksumMismatch(RuntimeError):
    pass


def verify_checksum(cases_path: Path) -> None:
    actual = hashlib.sha256(cases_path.read_bytes()).hexdigest()
    checksum_path = cases_path.with_name("cases_v2.sha256")
    expected = checksum_path.read_text(encoding="utf-8").split()[0]
    if actual != expected:
        raise ChecksumMismatch(f"case checksum mismatch: expected {expected}, got {actual}; refusing to run")


def _sentence_result(inputs: dict[str, Any]) -> dict[str, Any]:
    try:
        result = validate_claims(inputs["paper_text"], inputs["items"])
        accepted = [asdict(item) for item in result.accepted]
        rejected = [asdict(item) for item in result.rejected]
        return {
            "observed": len(accepted) == len(inputs["items"]),
            "accepted": accepted,
            "rejected": rejected,
            "raw_error": "; ".join(item["reason"] for item in rejected) or None,
        }
    except Exception as exc:
        return {"observed": False, "accepted": [], "rejected": [], "raw_error": str(exc)}


def _commit_result(inputs: dict[str, Any]) -> dict[str, Any]:
    repo = ROOT / inputs["repo_fixture"]
    try:
        prepared, resolved = prepare_repository(repo, inputs["commit_hash"], checkout=inputs["checkout"])
        return {"observed": True, "resolved_commit": resolved, "prepared_repo": str(prepared), "raw_error": None}
    except Exception as exc:
        return {"observed": False, "resolved_commit": None, "prepared_repo": str(repo), "raw_error": str(exc)}


def _location_result(inputs: dict[str, Any]) -> dict[str, Any]:
    repo = ROOT / inputs["repo_fixture"]
    try:
        location, error = validate_location(repo, inputs["item"])
        return {
            "observed": location is not None,
            "location": location.to_output() if location is not None else None,
            "raw_error": error,
        }
    except Exception as exc:
        return {"observed": False, "location": None, "raw_error": str(exc)}


def evaluate(case: dict[str, Any]) -> dict[str, Any]:
    inputs = case["validator_inputs"]
    if case["group"] == "sentence":
        observation = _sentence_result(inputs)
        validator = "validate_claims"
    elif case["group"] == "commit":
        observation = _commit_result(inputs)
        validator = "prepare_repository"
    elif case["group"] == "location":
        observation = _location_result(inputs)
        validator = "validate_location"
    else:
        observation = {"observed": False, "raw_error": f"unknown benchmark group: {case['group']}"}
        validator = "unknown"
    return {
        "case_id": case["case_id"],
        "group": case["group"],
        "mutation_type": case["mutation_type"],
        "expected_class": case["expected_class"],
        "rationale": case["rationale"],
        "validator": validator,
        "validator_inputs": inputs,
        **observation,
    }


def run_cases(cases_path: Path, output_path: Path) -> list[dict[str, Any]]:
    verify_checksum(cases_path)
    cases = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    results = [evaluate(case) for case in cases]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in results), encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the v2 adversarial benchmark against the project validators.")
    parser.add_argument("--cases", type=Path, default=ROOT / "benchmark" / "cases_v2.jsonl")
    parser.add_argument("--output", type=Path, default=ROOT / "benchmark" / "results_v2.jsonl")
    args = parser.parse_args()
    try:
        results = run_cases(args.cases, args.output)
    except ChecksumMismatch as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps({"cases": len(results), "results": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
