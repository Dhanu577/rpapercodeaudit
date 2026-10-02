import tempfile
import unittest
from pathlib import Path

from rpapercodeaudit.code_location import validate_location


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


if __name__ == "__main__":
    unittest.main()
