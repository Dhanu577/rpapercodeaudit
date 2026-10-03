from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from benchmark.generate_cases_v3 import TYPE_CLASSES

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "benchmark" / "cases_v3.jsonl"
CHECKSUM = ROOT / "benchmark" / "cases_v3.sha256"


def test_v3_cases_have_predeclared_labels_and_ten_per_mutation_type():
    rows = [json.loads(line) for line in CASES.read_text(encoding="utf-8").splitlines() if line.strip()]
    counts = Counter(row["mutation_type"] for row in rows)
    assert rows
    assert min(counts.values()) >= 10
    for row in rows:
        if row["mutation_type"] == "S_unicode_composition":
            sentence = row["validator_inputs"]["items"][0]["verbatim_sentence"]
            import unicodedata
            expected = "must_accept" if unicodedata.normalize("NFC", sentence) == sentence else "must_reject"
        else:
            expected = TYPE_CLASSES[row["mutation_type"]]
        assert row["expected_class"] == expected, row["case_id"]

    assert {row["expected_class"] for row in rows if row["mutation_type"] == "S_empty_or_whitespace"} == {"must_reject"}
    assert {row["expected_class"] for row in rows if row["mutation_type"] in {"S_one_word_substring", "S_four_word_sentence"}} == {"boundary"}
    assert {row["expected_class"] for row in rows if row["mutation_type"] == "S_exactly_five_words"} == {"must_accept"}


def test_v3_frozen_input_checksum_matches():
    expected = CHECKSUM.read_text(encoding="utf-8").split()[0]
    actual = hashlib.sha256(CASES.read_bytes()).hexdigest()
    assert actual == expected
