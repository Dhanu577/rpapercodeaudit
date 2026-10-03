import tempfile
import subprocess
import unittest
from pathlib import Path

from rpapercodeaudit.code_location import prepare_repository, validate_location


class CodeLocationValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "R").mkdir()
        (self.repo / "R" / "example.R").write_text(
            "foo <- function(x = 1) {\n  x + 1\n}\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def base_item(self):
        return {
            "claim_id": "C001",
            "package": "demoPkg",
            "commit_hash": "abc123",
            "code_file": "R/example.R",
            "start_line": 1,
            "end_line": 2,
            "code_excerpt": "foo <- function(x = 1) {\n  x + 1\n",
            "keywords": ["foo", "1"],
        }

    def test_real_excerpt_is_accepted(self):
        location, reason = validate_location(self.repo, self.base_item())
        self.assertIsNotNone(location)
        self.assertIsNone(reason)
        self.assertEqual(location.code_lines, "1-2")

    def test_altered_excerpt_is_rejected(self):
        item = self.base_item()
        item["code_excerpt"] = "foo <- function(x = 2) {\n  x + 1\n"
        location, reason = validate_location(self.repo, item)
        self.assertIsNone(location)
        self.assertIn("exactly match", reason)

    def test_wrong_line_range_is_rejected(self):
        item = self.base_item()
        item["start_line"] = 2
        item["end_line"] = 3
        location, reason = validate_location(self.repo, item)
        self.assertIsNone(location)
        self.assertIn("exactly match", reason)

    def test_location_requires_real_integer_line_numbers(self):
        class IntegerSubclass(int):
            pass

        valid = self.base_item()
        valid["start_line"] = IntegerSubclass(1)
        valid["end_line"] = IntegerSubclass(2)
        location, reason = validate_location(self.repo, valid)
        self.assertIsNotNone(location)
        self.assertIsNone(reason)

        for field in ("start_line", "end_line"):
            for value in (True, "1", 1.0, None):
                item = self.base_item()
                item[field] = value
                with self.subTest(field=field, value=value):
                    location, reason = validate_location(self.repo, item)
                    self.assertIsNone(location)
                    self.assertIn(f"{field} must be an integer", reason)

    def test_prepare_repository_accepts_only_full_hex_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True)
            (repo / "file.txt").write_text("fixture\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "file.txt"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "fixture"], check=True)
            commit_hash = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()

            prepared, resolved = prepare_repository(repo, commit_hash.upper(), checkout=False)
            self.assertEqual(prepared, repo.resolve())
            self.assertEqual(resolved, commit_hash)

            invalid = ("", None, "a" * 39, "a" * 41, "g" * 40, commit_hash[:8], "main", "HEAD", "HEAD~1", "release-tag")
            for value in invalid:
                with self.subTest(value=value):
                    with self.assertRaisesRegex(ValueError, "40 hexadecimal"):
                        prepare_repository(repo, value, checkout=False)


if __name__ == "__main__":
    unittest.main()
