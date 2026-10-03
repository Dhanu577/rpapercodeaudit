from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "benchmark"


def test_case_checksum_matches_frozen_file():
    cases = BENCH / "cases.jsonl"
    checksum = hashlib.sha256(cases.read_bytes()).hexdigest()
    assert checksum == (BENCH / "cases.sha256").read_text().split()[0]


def test_cases_have_expected_tiers_and_labels():
    rows = [json.loads(line) for line in (BENCH / "cases.jsonl").read_text().splitlines() if line]
    assert rows
    assert any(r["tier"] == "A" and r["mutation_type"] == "A0_valid" and r["expected_valid"] for r in rows)
    assert any(r["tier"] == "B" and r["expected_valid"] for r in rows)
    assert all(r["seed"] == 42 for r in rows)
    assert all("expected_failing_stage" in r for r in rows)


def test_runner_refuses_tampered_checksum(tmp_path):
    cases = tmp_path / "cases.jsonl"; cases.write_text((BENCH / "cases.jsonl").read_text() + "\n")
    (tmp_path / "cases.sha256").write_text("0" * 64 + "  cases.jsonl\n")
    result = subprocess.run([sys.executable, str(BENCH / "run_validator.py"), "--cases", str(cases), "--repo", str(ROOT / "examples/deseq2/repo"), "--paper", str(ROOT / "examples/deseq2/DESeq.txt"), "--output-dir", str(tmp_path)], capture_output=True, text=True)
    assert result.returncode != 0
    assert "checksum mismatch" in (result.stdout + result.stderr)


def test_case_generation_reproducible(tmp_path):
    out1 = tmp_path / "one.jsonl"; out2 = tmp_path / "two.jsonl"
    command = [sys.executable, str(BENCH / "generate_cases.py"), "--output"]
    subprocess.run(command + [str(out1)], check=True, cwd=ROOT)
    subprocess.run(command + [str(out2)], check=True, cwd=ROOT)
    assert out1.read_bytes() == out2.read_bytes()


def test_wrapper_imports_and_calls_real_validators(tmp_path, monkeypatch):
    import benchmark.run_validator as runner
    from rpapercodeaudit import claim_extraction, code_location

    assert runner.validate_claims is claim_extraction.validate_claims
    assert runner.prepare_repository is code_location.prepare_repository
    assert runner.validate_location is code_location.validate_location

    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Benchmark Test"], check=True)
    source = "value <- 1\n"
    (repo / "example.R").write_text(source)
    subprocess.run(["git", "-C", str(repo), "add", "example.R"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "fixture"], check=True, capture_output=True, text=True)
    commit = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    monkeypatch.setattr(runner, "PINNED_COMMIT", commit)

    calls = []
    real_validate_claims = claim_extraction.validate_claims
    real_prepare_repository = code_location.prepare_repository
    real_validate_location = code_location.validate_location

    def record_claims(*args, **kwargs):
        calls.append("validate_claims")
        return real_validate_claims(*args, **kwargs)

    def record_prepare(*args, **kwargs):
        calls.append("prepare_repository")
        return real_prepare_repository(*args, **kwargs)

    def record_location(*args, **kwargs):
        calls.append("validate_location")
        return real_validate_location(*args, **kwargs)

    monkeypatch.setattr(runner, "validate_claims", record_claims)
    monkeypatch.setattr(runner, "prepare_repository", record_prepare)
    monkeypatch.setattr(runner, "validate_location", record_location)

    case = {
        "case_id": "test-case",
        "paper_sentence": "A verbatim sentence.",
        "commit": commit,
        "repo": "fixture",
        "file": "example.R",
        "line_start": 1,
        "line_end": 1,
        "excerpt": source,
    }
    result = runner.evaluate(case, "A verbatim sentence.", repo)

    assert calls == ["validate_claims", "prepare_repository", "validate_location"]
    assert result["stage_results"] == {
        "sentence_match": True,
        "repo_commit_valid": True,
        "location": True,
    }
    assert result["final_decision"] is True
