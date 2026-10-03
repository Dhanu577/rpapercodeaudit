from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import subprocess
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "benchmark"
SEED = 42
SOURCE_REPO_REL = "benchmark/fixtures/build/source_repo"

# These labels are assigned from VALIDATOR_SPEC.md, before running the validator.
TYPE_CLASSES = {
    "S_extra_whitespace": "must_accept",
    "S_duplicate_sentence": "must_accept",
    "S_sentence_boundary": "must_accept",
    "S_changed_case": "must_reject",
    "S_changed_punctuation": "must_reject",
    "S_smart_quotes": "must_reject",
    "S_hyphen_variants": "must_reject",
    "S_word_removed_or_reordered": "must_reject",
    "S_extra_word": "must_reject",
    "S_nonbreaking_space": "must_accept",
    "S_zero_width_character": "must_reject",
    "S_empty_or_whitespace": "must_reject",
    "S_one_word_substring": "must_reject",
    "S_four_word_sentence": "must_reject",
    "S_exactly_five_words": "must_accept",
    "C_full_hash": "must_accept",
    "C_nonexistent_hash": "must_reject",
    "C_empty_hash": "must_reject",
    "C_random_hex": "must_reject",
    "C_foreign_repository_hash": "must_reject",
    "C_short_hash": "must_reject",
    "C_ambiguous_short_hash": "must_reject",
    "C_uppercase_hash": "must_accept",
    "C_branch_name": "must_reject",
    "C_tag_name": "must_reject",
    "C_HEAD": "must_reject",
    "C_HEAD_parent": "must_reject",
    "C_39_character_hash": "must_reject",
    "C_41_character_hash": "must_reject",
    "C_nonhex_40_character_hash": "must_reject",
    "L_correct_single_line": "must_accept",
    "L_correct_multiline": "must_accept",
    "L_duplicate_code_two_places": "must_accept",
    "L_same_text_different_file": "must_accept",
    "L_path_traversal": "must_reject",
    "L_absolute_outside": "must_reject",
    "L_symlink_outside": "must_reject",
    "L_nonexistent_file": "must_reject",
    "L_directory_not_file": "must_reject",
    "L_partial_excerpt": "must_reject",
    "L_superset_excerpt": "must_reject",
    "L_start_after_end": "must_reject",
    "L_nonpositive_start": "must_reject",
    "L_end_beyond_eof": "must_reject",
    "L_missing_keys": "must_reject",
    "L_none_values": "must_reject",
    "L_crlf_lf": "boundary",
    "L_trailing_whitespace": "must_reject",
    "L_tab_vs_spaces": "boundary",
    "L_filename_case": "boundary",
    "L_line_number_coercion": "must_reject",
    "L_int_subclass_line_number": "boundary",
    "L_binary_file": "boundary",
    "L_empty_file": "must_reject",
    "L_no_final_newline": "must_accept",
    "L_outside_indexed_directories": "boundary",
    "L_large_line_number": "must_reject",
}

RATIONALES = {
    "must_accept": "The input satisfies the literal contract in VALIDATOR_SPEC.md.",
    "must_reject": "The input violates the literal contract in VALIDATOR_SPEC.md.",
    "boundary": "This is an explicitly retained/documented boundary case in VALIDATOR_SPEC.md; it is not scored as a required decision.",
}


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    )
    return completed.stdout.strip()


def prepare_worktree(source_repo: Path, case_id: str, start_commit: str) -> str:
    relative = f"benchmark/fixtures/build/v3_worktrees/{case_id}"
    target = ROOT / relative
    if target.exists():
        subprocess.run(
            ["git", "-C", str(source_repo), "worktree", "remove", "--force", str(target)],
            check=False, capture_output=True, text=True,
        )
        shutil.rmtree(target, ignore_errors=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "-C", str(source_repo), "worktree", "add", "--quiet", "--detach", str(target), start_commit],
        check=True, capture_output=True, text=True,
    )
    return relative


def label_for(case: dict[str, Any]) -> str:
    mutation = case["mutation_type"]
    if mutation == "S_unicode_composition":
        sentence = case["validator_inputs"]["items"][0]["verbatim_sentence"]
        return "must_accept" if unicodedata.normalize("NFC", sentence) == sentence else "must_reject"
    try:
        return TYPE_CLASSES[mutation]
    except KeyError as exc:
        raise ValueError(f"No predeclared v3 label for mutation type {mutation!r}") from exc


def transform_v2_cases(source_path: Path) -> list[dict[str, Any]]:
    cases = [json.loads(line) for line in source_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for case in cases:
        case["expected_class"] = label_for(case)
        case["rationale"] = RATIONALES[case["expected_class"]]
    return cases


def add_sentence_cases(cases: list[dict[str, Any]]) -> None:
    seed_case = next(case for case in cases if case["group"] == "sentence")
    paper_text = seed_case["validator_inputs"]["paper_text"]
    four_word = [
        "The model uses a",
        "model uses a 'zero-centred",
        "and estimates its width.",
        "The procedure then ends",
        "This supports the model",
    ]
    five_word = [
        "The model uses a 'zero-centred",
        "The procedure then ends here.",
        "The café item is stored",
        "This supports the model in",
        "and estimates its width. The",
    ]
    for label, variants, mutation in (
        ("four", four_word, "S_four_word_sentence"),
        ("five", five_word, "S_exactly_five_words"),
    ):
        for index in range(10):
            sentence = variants[index % len(variants)]
            case_id = f"S-{label}-word-{index:02d}"
            item = {
                "id": case_id,
                "verbatim_sentence": sentence,
                "section_or_figure": "Synthetic fixture",
                "claim_type": "other",
                "what_to_look_for": "Literal sentence validation",
            }
            cases.append({
                "case_id": case_id,
                "group": "sentence",
                "mutation_type": mutation,
                "expected_class": TYPE_CLASSES[mutation],
                "validator_inputs": {"paper_text": paper_text, "items": [item]},
                "rationale": RATIONALES[TYPE_CLASSES[mutation]],
            })


def add_invalid_hash_cases(cases: list[dict[str, Any]], source_repo: Path, valid_hash: str) -> None:
    head = git(source_repo, "rev-parse", "HEAD")
    variants = {
        "C_39_character_hash": [valid_hash[:-1]] * 10,
        "C_41_character_hash": [valid_hash + str(index) for index in range(10)],
        "C_nonhex_40_character_hash": [valid_hash[:index] + "g" + valid_hash[index + 1:] for index in range(10)],
    }
    for mutation, refs in variants.items():
        for index, commit_hash in enumerate(refs):
            case_id = f"{mutation}-{index:02d}"
            repo_fixture = prepare_worktree(source_repo, case_id, head)
            cases.append({
                "case_id": case_id,
                "group": "commit",
                "mutation_type": mutation,
                "expected_class": TYPE_CLASSES[mutation],
                "validator_inputs": {"repo_fixture": repo_fixture, "commit_hash": commit_hash, "checkout": True},
                "rationale": RATIONALES[TYPE_CLASSES[mutation]],
            })


def add_int_subclass_cases(cases: list[dict[str, Any]]) -> None:
    seed = next(case for case in cases if case["mutation_type"] == "L_correct_single_line")
    for index in range(10):
        item = dict(seed["validator_inputs"]["item"])
        line = int(item["start_line"])
        item["start_line"] = {"$line_type": "int_subclass", "value": line}
        item["end_line"] = {"$line_type": "int_subclass", "value": line}
        case_id = f"L-int-subclass-{index:02d}"
        cases.append({
            "case_id": case_id,
            "group": "location",
            "mutation_type": "L_int_subclass_line_number",
            "expected_class": "boundary",
            "validator_inputs": {"repo_fixture": seed["validator_inputs"]["repo_fixture"], "item": item},
            "rationale": RATIONALES["boundary"],
        })


def generate(source_path: Path, output_path: Path) -> list[dict[str, Any]]:
    cases = transform_v2_cases(source_path)
    add_sentence_cases(cases)
    source_repo = ROOT / SOURCE_REPO_REL
    valid_case = next(case for case in cases if case["mutation_type"] == "C_full_hash")
    valid_hash = valid_case["validator_inputs"]["commit_hash"].lower()
    add_invalid_hash_cases(cases, source_repo, valid_hash)
    add_int_subclass_cases(cases)
    random.Random(SEED).shuffle(cases)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "".join(json.dumps(case, sort_keys=True, ensure_ascii=False) + "\n" for case in cases),
        encoding="utf-8",
    )
    checksum = hashlib.sha256(output_path.read_bytes()).hexdigest()
    output_path.with_suffix(".sha256").write_text(f"{checksum}  {output_path.name}\n", encoding="utf-8")
    return cases


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the frozen, spec-labeled v3 case file; no validators are called.")
    parser.add_argument("--source", type=Path, default=BENCHMARK / "cases_v2.jsonl")
    parser.add_argument("--output", type=Path, default=BENCHMARK / "cases_v3.jsonl")
    args = parser.parse_args()
    cases = generate(args.source, args.output)
    print(json.dumps({"cases": len(cases), "seed": SEED, "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
