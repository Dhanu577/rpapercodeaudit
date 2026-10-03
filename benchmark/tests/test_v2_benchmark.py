from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "benchmark"


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_v2_labels_follow_the_predeclared_mutation_classes():
    from benchmark.generate_cases_v2 import MUTATION_CLASSES

    rows = read_jsonl(BENCH / "cases_v2.jsonl")
    assert {row["expected_class"] for row in rows} == {"must_accept", "must_reject", "boundary"}
    assert all(row["expected_class"] == MUTATION_CLASSES[row["mutation_type"]] for row in rows)
    assert all(isinstance(row["rationale"], str) and row["rationale"].endswith(".") for row in rows)
    counts = Counter(row["mutation_type"] for row in rows)
    assert counts and min(counts.values()) >= 10
    assert all({"case_id", "group", "mutation_type", "expected_class", "validator_inputs", "rationale"} <= row.keys() for row in rows)


def test_v2_generator_is_reproducible_with_seed_42(tmp_path):
    subprocess.run([sys.executable, str(BENCH / "fixtures" / "build_fixtures.py")], check=True, cwd=ROOT, capture_output=True, text=True)
    outputs = [tmp_path / "first" / "cases_v2.jsonl", tmp_path / "second" / "cases_v2.jsonl"]
    for output in outputs:
        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, str(BENCH / "generate_cases_v2.py"), "--output", str(output)], check=True, cwd=ROOT, capture_output=True, text=True)
    assert outputs[0].read_bytes() == outputs[1].read_bytes()
    checksums = [output.with_name("cases_v2.sha256").read_text().split()[0] for output in outputs]
    assert checksums[0] == checksums[1] == hashlib.sha256(outputs[0].read_bytes()).hexdigest()


def test_v2_runner_refuses_a_checksum_mismatch(tmp_path):
    cases = tmp_path / "cases_v2.jsonl"
    cases.write_bytes((BENCH / "cases_v2.jsonl").read_bytes() + b"\n")
    cases.with_name("cases_v2.sha256").write_text((BENCH / "cases_v2.sha256").read_text(), encoding="utf-8")
    output = tmp_path / "should_not_exist.jsonl"
    result = subprocess.run(
        [sys.executable, str(BENCH / "run_validator_v2.py"), "--cases", str(cases), "--output", str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "case checksum mismatch" in (result.stdout + result.stderr)
    assert not output.exists()
