from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parent
BUILD_DIR = FIXTURE_DIR / "build"
SOURCE_REPO = BUILD_DIR / "source_repo"
FOREIGN_REPO = BUILD_DIR / "foreign_repo"
MANIFEST = BUILD_DIR / "manifest.json"
OUTSIDE_DIR = Path("/tmp/benchmark-adversarial-v2-outside")


def run_git(repo: Path, *args: str, input_text: str | None = None, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        input=input_text,
        env={**os.environ, **(env or {})},
    )
    return completed.stdout.strip()


def init_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(path)], check=True)
    run_git(path, "config", "user.name", "Benchmark Fixture")
    run_git(path, "config", "user.email", "fixture@example.invalid")


def commit(repo: Path, message: str, day: int) -> str:
    date = f"2001-01-{day:02d}T00:00:00+0000"
    env = {"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
    run_git(repo, "add", "-A")
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-q", "-m", message],
        check=True,
        env={**os.environ, **env},
    )
    return run_git(repo, "rev-parse", "HEAD")


def add_ambiguous_commit_objects(repo: Path, count: int = 5) -> list[dict[str, str]]:
    """Write a few pairs of dangling commit objects with colliding 4-hex prefixes."""
    empty_tree = run_git(repo, "mktree", input_text="")
    first_by_prefix: dict[str, tuple[str, bytes]] = {}
    collisions: list[dict[str, str]] = []
    for nonce in range(250_000):
        body = (
            f"tree {empty_tree}\n"
            "author Fixture <fixture@example.invalid> 978307200 +0000\n"
            "committer Fixture <fixture@example.invalid> 978307200 +0000\n"
            f"\nambiguous-prefix-probe-{nonce}\n"
        ).encode("utf-8")
        object_id = hashlib.sha1(f"commit {len(body)}\0".encode("ascii") + body).hexdigest()
        prefix = object_id[:4]
        previous = first_by_prefix.get(prefix)
        if previous is None:
            first_by_prefix[prefix] = (object_id, body)
            continue
        if any(item["prefix"] == prefix for item in collisions):
            continue
        first_id, first_body = previous
        for expected, content in ((first_id, first_body), (object_id, body)):
            stored = run_git(repo, "hash-object", "-t", "commit", "-w", "--stdin", input_text=content.decode("utf-8"))
            if stored != expected:
                raise RuntimeError("Git returned an unexpected hash for a synthetic commit object")
        collisions.append({"prefix": prefix, "first": first_id, "second": object_id})
        if len(collisions) == count:
            return collisions
    raise RuntimeError(f"Could not construct {count} ambiguous commit prefixes")


def build_repository(repo: Path, foreign: bool = False) -> dict[str, object]:
    init_repo(repo)
    if foreign:
        (repo / "foreign.txt").write_text("A commit belonging only to the foreign repository.\n", encoding="utf-8")
        hashes = [commit(repo, "foreign root", 1)]
        for day in range(2, 13):
            (repo / "foreign.txt").write_text(f"Foreign repository revision {day}.\n", encoding="utf-8")
            hashes.append(commit(repo, f"foreign revision {day}", day))
        return {"commits": hashes, "head": hashes[-1]}

    (repo / "R").mkdir()
    (repo / "src").mkdir()
    (repo / "docs").mkdir()
    (repo / "R" / "folder").mkdir()
    sample_lines = [
        "The model uses a 'zero-centred prior', and estimates its width.\n",
        "The procedure then ends here.\n",
        "A café item is stored in composed form.\n",
        "Alpha\tbeta\n",
        "duplicate phrase\n",
        "middle marker\n",
        "duplicate phrase\n",
        "single final line without newline",
    ]
    (repo / "R" / "sample.txt").write_text("".join(sample_lines), encoding="utf-8")
    (repo / "src" / "sample.txt").write_text("".join(sample_lines), encoding="utf-8")
    (repo / "R" / "dup1.txt").write_text("shared code\nsecond shared line\n", encoding="utf-8")
    (repo / "R" / "dup2.txt").write_text("shared code\nsecond shared line\n", encoding="utf-8")
    (repo / "R" / "crlf.txt").write_bytes(b"crlf alpha\r\ncrlf beta\r\n")
    (repo / "R" / "empty.txt").write_bytes(b"")
    (repo / "R" / "binary.bin").write_bytes(b"\xff\x00\xfe\x80")
    (repo / "R" / "folder" / "child.txt").write_text("directory child\n", encoding="utf-8")
    (repo / "docs" / "outside_scope.txt").write_text("Outside indexed source directories.\n", encoding="utf-8")
    for index in range(10):
        directory = repo / "R" / f"folder-{index:02d}"
        directory.mkdir()
        (directory / "child.txt").write_text(f"Directory child {index}.\n", encoding="utf-8")
        (repo / "R" / f"empty-{index:02d}.txt").write_bytes(b"")
        (repo / "R" / f"binary-{index:02d}.bin").write_bytes(bytes((255, index, 254, 128)))
        (repo / "R" / f"no-final-{index:02d}.txt").write_bytes(f"no final newline {index}".encode("utf-8"))
        (repo / "docs" / f"outside-scope-{index:02d}.txt").write_text(f"Outside indexed source directories {index}.\n", encoding="utf-8")
    (repo / "R" / "numbers.txt").write_text("".join(f"number line {i}\n" for i in range(1, 21)), encoding="utf-8")
    for index in range(10):
        outside_file = OUTSIDE_DIR / f"outside-{index:02d}.txt"
        (repo / "R" / f"escape-{index:02d}.txt").symlink_to(outside_file)
    (repo / "R" / "tab_spaces.txt").write_text("left\tright\n", encoding="utf-8")
    (repo / "R" / "trailing.txt").write_text("trailing spaces   \n", encoding="utf-8")
    hashes = [commit(repo, "fixture root", 1)]
    for day in range(2, 13):
        (repo / "history").mkdir(exist_ok=True)
        (repo / "history" / f"revision-{day}.txt").write_text(f"Synthetic history revision {day}.\n", encoding="utf-8")
        hashes.append(commit(repo, f"fixture revision {day}", day))
    root_commit = hashes[0]
    run_git(repo, "branch", "feature-probe", root_commit)
    run_git(repo, "tag", "release-probe", hashes[1])
    for index in range(5):
        run_git(repo, "branch", f"branch-probe-{index}", hashes[index])
        run_git(repo, "tag", f"tag-probe-{index}", hashes[index + 1])
    ambiguous = add_ambiguous_commit_objects(repo)
    return {
        "commits": hashes,
        "head": hashes[-1],
        "root": root_commit,
        "feature": root_commit,
        "tag": hashes[1],
        "ambiguous_prefixes": ambiguous,
        "outside_file": str(outside_file),
    }


def main() -> None:
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True)
    if OUTSIDE_DIR.exists():
        shutil.rmtree(OUTSIDE_DIR)
    OUTSIDE_DIR.mkdir(parents=True)
    for index in range(10):
        (OUTSIDE_DIR / f"outside-{index:02d}.txt").write_text(f"Target outside the synthetic repository {index}.\n", encoding="utf-8")
    manifest = {
        "source_repo": str(SOURCE_REPO.relative_to(FIXTURE_DIR.parents[1])).replace("\\", "/"),
        "foreign_repo": str(FOREIGN_REPO.relative_to(FIXTURE_DIR.parents[1])).replace("\\", "/"),
        "source": build_repository(SOURCE_REPO),
        "foreign": build_repository(FOREIGN_REPO, foreign=True),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"source_commits": len(manifest["source"]["commits"]), "ambiguous_prefixes": [x["prefix"] for x in manifest["source"]["ambiguous_prefixes"]], "manifest": str(MANIFEST)}, indent=2))


if __name__ == "__main__":
    main()
