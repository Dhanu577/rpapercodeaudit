from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from random import Random
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "benchmark" / "fixtures"
BUILD_DIR = FIXTURE_DIR / "build"
MANIFEST_PATH = BUILD_DIR / "manifest.json"
SEED = 42
LABELS = ("must_accept", "must_reject", "boundary")

MUTATION_CLASSES = {
    "S_extra_whitespace": "must_accept",
    "S_duplicate_sentence": "must_accept",
    "S_sentence_boundary": "must_accept",
    "S_changed_case": "must_reject",
    "S_changed_punctuation": "must_reject",
    "S_smart_quotes": "must_reject",
    "S_hyphen_variants": "must_reject",
    "S_word_removed_or_reordered": "must_reject",
    "S_extra_word": "must_reject",
    "S_nonbreaking_space": "boundary",
    "S_zero_width_character": "boundary",
    "S_unicode_composition": "boundary",
    "S_empty_or_whitespace": "boundary",
    "S_one_word_substring": "boundary",
    "C_full_hash": "must_accept",
    "C_nonexistent_hash": "must_reject",
    "C_empty_hash": "must_reject",
    "C_random_hex": "must_reject",
    "C_foreign_repository_hash": "must_reject",
    "C_short_hash": "boundary",
    "C_ambiguous_short_hash": "boundary",
    "C_uppercase_hash": "boundary",
    "C_branch_name": "boundary",
    "C_tag_name": "boundary",
    "C_HEAD": "boundary",
    "C_HEAD_parent": "boundary",
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
    "L_trailing_whitespace": "boundary",
    "L_tab_vs_spaces": "boundary",
    "L_filename_case": "boundary",
    "L_line_number_coercion": "boundary",
    "L_binary_file": "boundary",
    "L_empty_file": "boundary",
    "L_no_final_newline": "boundary",
    "L_outside_indexed_directories": "boundary",
    "L_large_line_number": "boundary",
}

SENTENCE = "The model uses a 'zero-centred prior', and estimates its width."
SECOND_SENTENCE = "The procedure then ends here."
UNICODE_SENTENCE = "The café item is stored in composed form."
PAPER_TEXT = (
    f"{SENTENCE}\n{SECOND_SENTENCE}\n{SENTENCE}\n{UNICODE_SENTENCE}\n"
    "This supports the model in the next section.\n"
)
SOURCE_REPO_REL = "benchmark/fixtures/build/source_repo"


def git(repo: Path, *args: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def add_case(
    cases: list[dict[str, Any]], case_id: str, group: str, mutation_type: str,
    inputs: dict[str, Any], rationale: str,
) -> None:
    expected = MUTATION_CLASSES[mutation_type]
    cases.append({
        "case_id": case_id,
        "group": group,
        "mutation_type": mutation_type,
        "expected_class": expected,
        "validator_inputs": inputs,
        "rationale": rationale,
    })


def claim_inputs(verbatim_sentence: str, claim_id: str) -> dict[str, Any]:
    return {
        "paper_text": PAPER_TEXT,
        "items": [{
            "id": claim_id,
            "verbatim_sentence": verbatim_sentence,
            "section_or_figure": "Synthetic fixture",
            "claim_type": "other",
            "what_to_look_for": "Literal sentence validation",
        }],
    }


def prepare_worktree(source_repo: Path, case_id: str, start_commit: str) -> str:
    worktree_rel = f"benchmark/fixtures/build/worktrees/{case_id}"
    worktree = ROOT / worktree_rel
    worktree.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "-C", str(source_repo), "worktree", "add", "--quiet", "--detach", str(worktree), start_commit],
        check=True,
        capture_output=True,
        text=True,
    )
    return worktree_rel


def build_sentence_cases(cases: list[dict[str, Any]]) -> None:
    space_forms = ["  ", "\t", "\n", " \t ", "\n\t", "\t\n", "   ", "\r\n", "\t  ", " \n "]
    for index, separator in enumerate(space_forms):
        claim = SENTENCE.replace(" ", separator)
        add_case(cases, f"S-whitespace-{index:02d}", "sentence", "S_extra_whitespace", claim_inputs(claim, f"ws-{index}"), "Whitespace normalization maps internal runs to the sentence's original spaces.")
    for index in range(10):
        add_case(cases, f"S-duplicate-{index:02d}", "sentence", "S_duplicate_sentence", claim_inputs(SENTENCE, f"dup-{index}"), "The exact sentence occurs twice in the supplied paper text.")
    boundary_claim = "its width. The procedure then ends here."
    for index, separator in enumerate(space_forms):
        claim = f"its width.{separator}The procedure then ends here."
        add_case(cases, f"S-boundary-{index:02d}", "sentence", "S_sentence_boundary", claim_inputs(claim, f"boundary-{index}"), "The literal substring crosses a sentence boundary and whitespace normalization removes only its separator.")

    case_variants = [SENTENCE.replace("The model", "the model", 1) if i % 2 == 0 else SENTENCE.replace("width", "Width", 1) for i in range(10)]
    for index, claim in enumerate(case_variants):
        add_case(cases, f"S-case-{index:02d}", "sentence", "S_changed_case", claim_inputs(claim, f"case-{index}"), "Case folding is explicitly excluded, so the changed-case text is not an exact normalized substring.")
    for index in range(10):
        claim = SENTENCE.replace(",", "", 1) if index % 2 == 0 else SENTENCE[:-1] + ".."
        add_case(cases, f"S-punctuation-{index:02d}", "sentence", "S_changed_punctuation", claim_inputs(claim, f"punct-{index}"), "Punctuation is preserved by whitespace normalization and the edited text is not the same substring.")
    smart_quotes = [
        SENTENCE.replace("'zero-centred prior'", "‘zero-centred prior’"),
        SENTENCE.replace("'zero-centred prior'", "“zero-centred prior”"),
    ]
    for index in range(10):
        claim = smart_quotes[index % len(smart_quotes)]
        add_case(cases, f"S-quotes-{index:02d}", "sentence", "S_smart_quotes", claim_inputs(claim, f"quotes-{index}"), "Curly quotation marks differ from the straight marks in the paper substring.")
    hyphen_forms = ["zero–centred", "zero−centred", "zero—centred", "zero‐centred", "zero‑centred"]
    for index in range(10):
        claim = SENTENCE.replace("zero-centred", hyphen_forms[index % len(hyphen_forms)])
        add_case(cases, f"S-hyphen-{index:02d}", "sentence", "S_hyphen_variants", claim_inputs(claim, f"hyphen-{index}"), "The substituted dash code point is not normalized to the paper's hyphen.")
    edits = [
        SENTENCE.replace("zero-centred ", "", 1),
        SENTENCE.replace("estimates ", "", 1),
        SENTENCE.replace("The model", "model The", 1),
        SENTENCE.replace("a 'zero-centred", "'zero-centred a", 1),
        SENTENCE.replace("its width", "width its", 1),
    ]
    for index in range(10):
        add_case(cases, f"S-word-edit-{index:02d}", "sentence", "S_word_removed_or_reordered", claim_inputs(edits[index % len(edits)], f"word-{index}"), "Removing or reordering a word changes the literal substring rather than merely its whitespace.")
    for index in range(10):
        claim = SENTENCE[:-1] + f" indeed{index}."
        add_case(cases, f"S-extra-word-{index:02d}", "sentence", "S_extra_word", claim_inputs(claim, f"extra-{index}"), "The appended word makes the claim longer than the paper's exact sentence substring.")

    nbsp_forms = [SENTENCE.replace(" ", "\u00a0")]
    for index in range(10):
        claim = nbsp_forms[0] if index % 2 == 0 else SENTENCE.replace(" model ", "\u00a0model\u00a0")
        add_case(cases, f"S-nbsp-{index:02d}", "sentence", "S_nonbreaking_space", claim_inputs(claim, f"nbsp-{index}"), "The specification does not define how non-breaking spaces interact with whitespace normalization.")
    for index in range(10):
        claim = SENTENCE.replace("model", f"mo\u200bdel", 1) if index % 2 == 0 else SENTENCE.replace("width", f"wi\u200bdth", 1)
        add_case(cases, f"S-zero-width-{index:02d}", "sentence", "S_zero_width_character", claim_inputs(claim, f"zwsp-{index}"), "The specification does not state whether zero-width characters are normalized.")
    for index in range(10):
        composed = UNICODE_SENTENCE
        decomposed = "The cafe\u0301 item is stored in composed form."
        claim = decomposed if index % 2 == 0 else composed
        add_case(cases, f"S-unicode-{index:02d}", "sentence", "S_unicode_composition", claim_inputs(claim, f"unicode-{index}"), "The specification does not define Unicode normalization beyond whitespace.")
    for index in range(10):
        claim = "" if index % 2 == 0 else " \t\n "
        add_case(cases, f"S-empty-{index:02d}", "sentence", "S_empty_or_whitespace", claim_inputs(claim, f"empty-{index}"), "The specification does not clarify whether an empty normalized claim is a meaningful substring.")
    for index in range(10):
        add_case(cases, f"S-one-word-{index:02d}", "sentence", "S_one_word_substring", claim_inputs("the", f"one-word-{index}"), "The specification does not clarify whether an ordinary one-word substring is a valid sentence claim.")


def build_commit_cases(cases: list[dict[str, Any]], manifest: dict[str, Any]) -> None:
    source_repo = ROOT / manifest["source_repo"]
    source = manifest["source"]
    foreign = manifest["foreign"]
    commits = list(source["commits"])
    head = str(source["head"])
    target_pairs = [(commits[i], i) for i in range(5)]

    def add_commit(mutation: str, case_id: str, commit_ref: str, checkout: bool, start_commit: str, rationale: str) -> None:
        repo_fixture = prepare_worktree(source_repo, case_id, start_commit)
        add_case(cases, case_id, "commit", mutation, {
            "repo_fixture": repo_fixture,
            "commit_hash": commit_ref,
            "checkout": checkout,
        }, rationale)

    for index, (commit_hash, _) in enumerate(target_pairs):
        for checkout in (True, False):
            case_id = f"C-full-{index:02d}-checkout-{str(checkout).lower()}"
            start = head if checkout else commit_hash
            add_commit("C_full_hash", case_id, commit_hash, checkout, start, "A full object hash resolves to an existing commit; the isolated repository starts at that commit for the no-checkout call.")

    missing_hashes = [hashlib.sha1(f"missing-commit-{i}".encode()).hexdigest() for i in range(5)]
    for mutation, refs, rationale in [
        ("C_nonexistent_hash", missing_hashes, "The syntactically valid object id is not present in the synthetic repository."),
        ("C_empty_hash", [""] * 5, "An empty commit reference does not identify a commit object."),
        ("C_random_hex", [hashlib.sha1(f"random-hex-{i}".encode()).hexdigest() for i in range(5)], "The random hexadecimal object id is absent from the synthetic repository."),
        ("C_foreign_repository_hash", list(foreign["commits"][:5]), "The object id belongs to a separate repository and is not available in this repository's object database."),
    ]:
        for index, commit_ref in enumerate(refs):
            for checkout in (True, False):
                case_id = f"{mutation}-{index:02d}-checkout-{str(checkout).lower()}"
                add_commit(mutation, case_id, commit_ref, checkout, head, rationale)

    for mutation, references, starting in [
        ("C_short_hash", [str(value)[:8] for value in commits[:5]], commits[:5]),
        ("C_ambiguous_short_hash", [str(value["prefix"]) for value in source["ambiguous_prefixes"]], [head] * 5),
        ("C_uppercase_hash", [str(value).upper() for value in commits[:5]], commits[:5]),
        ("C_branch_name", [f"branch-probe-{i}" for i in range(5)], [str(value) for value in source["commits"][:5]]),
        ("C_tag_name", [f"tag-probe-{i}" for i in range(5)], [str(value) for value in source["commits"][1:6]]),
        ("C_HEAD", ["HEAD"] * 5, commits[:5]),
        ("C_HEAD_parent", ["HEAD~1"] * 5, commits[1:6]),
    ]:
        for index, (commit_ref, target) in enumerate(zip(references, starting)):
            for checkout in (True, False):
                case_id = f"{mutation}-{index:02d}-checkout-{str(checkout).lower()}"
                start_commit = head if checkout else str(target)
                rationale = "The documented commit API does not specify whether this abbreviated or symbolic reference resolves or how checkout mode affects it."
                add_commit(mutation, case_id, commit_ref, checkout, start_commit, rationale)


def location_inputs(item: dict[str, Any]) -> dict[str, Any]:
    return {"repo_fixture": SOURCE_REPO_REL, "item": item}


def make_item(code_file: Any, start_line: Any, end_line: Any, excerpt: Any, **extra: Any) -> dict[str, Any]:
    return {
        "claim_id": "location-probe",
        "package": "synthetic-fixture",
        "commit_hash": "fixture-static-text",
        "code_file": code_file,
        "start_line": start_line,
        "end_line": end_line,
        "code_excerpt": excerpt,
        **extra,
    }


def build_location_cases(cases: list[dict[str, Any]], manifest: dict[str, Any]) -> None:
    source_repo = ROOT / manifest["source_repo"]
    sample = (source_repo / "R" / "sample.txt").read_text(encoding="utf-8").splitlines(keepends=True)
    numbers = (source_repo / "R" / "numbers.txt").read_text(encoding="utf-8").splitlines(keepends=True)

    for index in range(10):
        start = index % len(sample) + 1
        item = make_item("R/sample.txt", start, start, sample[start - 1])
        add_case(cases, f"L-single-{index:02d}", "location", "L_correct_single_line", location_inputs(item), "The cited one-line excerpt exactly equals the on-disk line in the cited file.")
    for index in range(10):
        start = index % (len(sample) - 1) + 1
        end = start + 1
        item = make_item("R/sample.txt", start, end, "".join(sample[start - 1:end]))
        add_case(cases, f"L-multiline-{index:02d}", "location", "L_correct_multiline", location_inputs(item), "The cited multi-line excerpt exactly equals the inclusive on-disk range.")
    for index in range(10):
        filename = "R/dup1.txt" if index % 2 == 0 else "R/dup2.txt"
        item = make_item(filename, 1, 2, "shared code\nsecond shared line\n")
        add_case(cases, f"L-duplicate-code-{index:02d}", "location", "L_duplicate_code_two_places", location_inputs(item), "The cited file contains the exact range even though identical text occurs at a second location.")
    for index in range(10):
        filename = "src/sample.txt" if index % 2 == 0 else "R/sample.txt"
        start = index % len(sample) + 1
        item = make_item(filename, start, start, sample[start - 1])
        add_case(cases, f"L-same-text-file-{index:02d}", "location", "L_same_text_different_file", location_inputs(item), "The cited file itself contains the exact excerpt, regardless of identical text in another file.")

    outside_paths = [f"../outside-{i:02d}.txt" if i % 2 == 0 else f"R/../../outside-{i:02d}.txt" for i in range(10)]
    for index, path in enumerate(outside_paths):
        item = make_item(path, 1, 1, f"Target outside the synthetic repository {index}.\n")
        add_case(cases, f"L-traversal-{index:02d}", "location", "L_path_traversal", location_inputs(item), "Resolving the relative path places it outside the repository root.")
    for index in range(10):
        outside = f"/tmp/benchmark-adversarial-v2-outside/outside-{index:02d}.txt"
        item = make_item(outside, 1, 1, f"Target outside the synthetic repository {index}.\n")
        add_case(cases, f"L-absolute-outside-{index:02d}", "location", "L_absolute_outside", location_inputs(item), "The absolute cited path resolves outside the repository root.")
    for index in range(10):
        item = make_item(f"R/escape-{index:02d}.txt", 1, 1, f"Target outside the synthetic repository {index}.\n")
        add_case(cases, f"L-symlink-outside-{index:02d}", "location", "L_symlink_outside", location_inputs(item), "The in-repository symlink resolves to a target outside the repository root.")
    for index in range(10):
        item = make_item(f"R/__missing-{index:02d}.txt", 1, 1, "missing\n")
        add_case(cases, f"L-missing-file-{index:02d}", "location", "L_nonexistent_file", location_inputs(item), "The cited path does not name a file in the synthetic repository.")
    for index in range(10):
        item = make_item(f"R/folder-{index:02d}", 1, 1, "directory\n")
        add_case(cases, f"L-directory-{index:02d}", "location", "L_directory_not_file", location_inputs(item), "The cited path is a directory rather than a readable file.")
    for index in range(10):
        start = index % (len(sample) - 1) + 1
        item = make_item("R/sample.txt", start, start + 1, sample[start - 1])
        add_case(cases, f"L-partial-{index:02d}", "location", "L_partial_excerpt", location_inputs(item), "The excerpt contains only part of the cited two-line range.")
    for index in range(10):
        start = index % (len(sample) - 1) + 1
        item = make_item("R/sample.txt", start, start, "".join(sample[start - 1:start + 1]))
        add_case(cases, f"L-superset-{index:02d}", "location", "L_superset_excerpt", location_inputs(item), "The supplied excerpt includes text beyond the cited one-line range.")
    for index in range(10):
        start = 2 + index
        item = make_item("R/numbers.txt", start, 1, numbers[start - 1])
        add_case(cases, f"L-start-after-end-{index:02d}", "location", "L_start_after_end", location_inputs(item), "The requested start line is greater than the requested end line.")
    for index in range(10):
        start = 0 if index % 2 == 0 else -index
        item = make_item("R/sample.txt", start, 1, sample[0])
        add_case(cases, f"L-nonpositive-start-{index:02d}", "location", "L_nonpositive_start", location_inputs(item), "A zero or negative start line lies outside the file's one-based line range.")
    for index in range(10):
        end = 21 + index
        item = make_item("R/numbers.txt", 20, end, numbers[-1])
        add_case(cases, f"L-end-beyond-{index:02d}", "location", "L_end_beyond_eof", location_inputs(item), "The requested end line is beyond the file's final line.")
    required = make_item("R/sample.txt", 1, 1, sample[0])
    required_keys = ("code_file", "start_line", "end_line", "code_excerpt")
    for index in range(10):
        item = dict(required)
        del item[required_keys[index % len(required_keys)]]
        add_case(cases, f"L-missing-key-{index:02d}", "location", "L_missing_keys", location_inputs(item), "A required location field is absent from the mapping.")
    none_fields = ("code_file", "start_line", "end_line", "code_excerpt")
    for index in range(10):
        item = dict(required)
        item[none_fields[index % len(none_fields)]] = None
        add_case(cases, f"L-none-{index:02d}", "location", "L_none_values", location_inputs(item), "A required location field is present with a None value rather than a valid input.")

    for index in range(10):
        excerpt = "crlf alpha\r\n" if index % 2 == 0 else "crlf alpha\n"
        item = make_item("R/crlf.txt", 1, 1, excerpt)
        add_case(cases, f"L-crlf-{index:02d}", "location", "L_crlf_lf", location_inputs(item), "The specification does not decide whether text-mode newline translation makes CRLF and LF excerpts equivalent.")
    for index in range(10):
        excerpt = "trailing spaces\n" if index % 2 == 0 else f"trailing spaces{' ' * (index % 4 + 1)}\n"
        item = make_item("R/trailing.txt", 1, 1, excerpt)
        add_case(cases, f"L-trailing-{index:02d}", "location", "L_trailing_whitespace", location_inputs(item), "The specification does not clarify whether trailing spaces are ignored during excerpt equality.")
    for index in range(10):
        excerpt = "left    right\n" if index % 2 == 0 else "left\tright\n"
        item = make_item("R/tab_spaces.txt", 1, 1, excerpt)
        add_case(cases, f"L-tab-spaces-{index:02d}", "location", "L_tab_vs_spaces", location_inputs(item), "The specification does not say whether tabs and spaces are interchangeable in exact excerpt comparison.")
    for index in range(10):
        filename = "R/Sample.txt" if index % 2 == 0 else "R/sample.txt"
        item = make_item(filename, 1, 1, sample[0])
        add_case(cases, f"L-name-case-{index:02d}", "location", "L_filename_case", location_inputs(item), "File-name case behavior can depend on the host filesystem and is recorded as a boundary.")
    for index in range(10):
        value: Any = ("10", 10.0, True, 1.0, "1")[index % 5]
        line = int(value)
        item = make_item("R/numbers.txt", value, line, numbers[line - 1])
        add_case(cases, f"L-line-type-{index:02d}", "location", "L_line_number_coercion", location_inputs(item), "The specification does not define coercion of strings, floats, or booleans to line numbers.")
    for index in range(10):
        item = make_item(f"R/binary-{index:02d}.bin", 1, 1, "")
        add_case(cases, f"L-binary-{index:02d}", "location", "L_binary_file", location_inputs(item), "The specification does not describe how a text validator handles binary file contents.")
    for index in range(10):
        item = make_item(f"R/empty-{index:02d}.txt", 1, 1, "")
        add_case(cases, f"L-empty-file-{index:02d}", "location", "L_empty_file", location_inputs(item), "The specification does not define a valid citation range for an empty file.")
    for index in range(10):
        file = f"R/no-final-{index:02d}.txt"
        text = (source_repo / file).read_text(encoding="utf-8")
        item = make_item(file, 1, 1, text)
        add_case(cases, f"L-no-final-newline-{index:02d}", "location", "L_no_final_newline", location_inputs(item), "The specification does not explicitly address exact excerpts from a final line without a newline.")
    for index in range(10):
        file = f"docs/outside-scope-{index:02d}.txt"
        text = (source_repo / file).read_text(encoding="utf-8")
        item = make_item(file, 1, 1, text)
        add_case(cases, f"L-outside-index-{index:02d}", "location", "L_outside_indexed_directories", location_inputs(item), "The specification does not say whether location validation restricts files to indexing directories.")
    for index in range(10):
        item = make_item("R/numbers.txt", 1_000_000 + index, 1_000_000 + index, "unreachable\n")
        add_case(cases, f"L-large-line-{index:02d}", "location", "L_large_line_number", location_inputs(item), "The specification does not characterize extremely large line-number inputs.")


def generate(output: Path) -> list[dict[str, Any]]:
    if not MANIFEST_PATH.is_file():
        raise SystemExit("synthetic fixtures are missing; run python3 benchmark/fixtures/build_fixtures.py first")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    source_repo = ROOT / manifest["source_repo"]
    worktrees = BUILD_DIR / "worktrees"
    if worktrees.exists():
        shutil.rmtree(worktrees)
    git(source_repo, "worktree", "prune", "--expire=now")
    cases: list[dict[str, Any]] = []
    build_sentence_cases(cases)
    build_commit_cases(cases, manifest)
    build_location_cases(cases, manifest)
    Random(SEED).shuffle(cases)
    counts = Counter(row["mutation_type"] for row in cases)
    if set(row["expected_class"] for row in cases) != set(LABELS):
        raise AssertionError("case generation failed to include the three declared label classes")
    if any(count < 10 for count in counts.values()):
        raise AssertionError(f"mutation types below the ten-case target: {counts}")
    output.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in cases)
    output.write_text(text, encoding="utf-8")
    checksum_path = output.with_name("cases_v2.sha256")
    checksum_path.write_text(f"{hashlib.sha256(text.encode('utf-8')).hexdigest()}  {output.name}\n", encoding="utf-8")
    print(json.dumps({
        "cases": len(cases),
        "classes": dict(Counter(row["expected_class"] for row in cases)),
        "mutation_types": len(counts),
        "minimum_per_mutation_type": min(counts.values()),
        "checksum": checksum_path.read_text(encoding="utf-8").split()[0],
        "seed": SEED,
    }, indent=2))
    return cases


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "benchmark" / "cases_v2.jsonl")
    args = parser.parse_args()
    generate(args.output)


if __name__ == "__main__":
    main()
