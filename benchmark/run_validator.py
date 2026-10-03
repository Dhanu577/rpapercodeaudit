from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rpapercodeaudit.claim_extraction import extract_claims, normalize_whitespace

PINNED_COMMIT = "76c5f8523716804dbe0a9500b4b7e216c6af225c"


def git(repo: Path, *args: str) -> tuple[bool, str]:
    p = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True)
    return p.returncode == 0, p.stdout.strip() if p.returncode == 0 else p.stderr.strip()


def blob(repo: Path, commit: str, file: str) -> str | None:
    ok, _ = git(repo, "cat-file", "-e", f"{commit}:{file}")
    if not ok:
        return None
    ok, output = git(repo, "show", f"{commit}:{file}")
    return output if ok else None


def evaluate(case: dict[str, Any], paper: str, repo: Path) -> dict[str, Any]:
    sentence_match = normalize_whitespace(case["paper_sentence"]) in normalize_whitespace(paper)
    commit_resolves, commit_value = git(repo, "rev-parse", "--verify", f"{case['commit']}^{{commit}}")
    repo_commit_valid = commit_resolves and commit_value == PINNED_COMMIT
    content = blob(repo, case["commit"], case["file"]) if commit_resolves else None
    file_exists = content is not None
    lines = content.splitlines(keepends=True) if content is not None else []
    start, end = int(case["line_start"]), int(case["line_end"])
    line_range_valid = file_exists and start >= 1 and end >= start and end <= len(lines)
    actual = "".join(lines[start - 1:end]) if line_range_valid else ""
    excerpt_matches = line_range_valid and normalize_whitespace(actual) == normalize_whitespace(case["excerpt"])
    stages = {"sentence_match": sentence_match, "repo_commit_valid": repo_commit_valid, "file_exists": file_exists, "line_range_valid": line_range_valid, "excerpt_matches": excerpt_matches}
    first_failure = next((name for name, passed in stages.items() if not passed), None)
    return {**case, "stage_results": stages, "final_decision": all(stages.values()), "first_failing_stage": first_failure, "mode": "mechanical"}


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
