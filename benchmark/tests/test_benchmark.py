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
