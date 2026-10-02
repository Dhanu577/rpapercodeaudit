import csv
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from rpapercodeaudit.export import export_csv, export_xlsx
from rpapercodeaudit.schema import ClaimRecord, SCHEMA_FIELDS


class SchemaExportTests(unittest.TestCase):
    def sample(self) -> ClaimRecord:
        return ClaimRecord(
            id="C001",
            package="demoPkg",
            commit_hash="abc123",
            paper_sentence="The method filters genes below 10 counts.",
            paper_section="Methods",
            claim_type="filtering",
            expected_implementation="filter threshold 10",
            verdict="not verified",
            checked_by_me=False,
        )

    def test_csv_has_canonical_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = export_csv([self.sample()], Path(tmp) / "claims.csv")
            with path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["id"], "C001")
            self.assertEqual(list(rows[0]), list(SCHEMA_FIELDS))

    def test_xlsx_has_dropdown_freeze_and_summary_countif(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = export_xlsx([self.sample()], Path(tmp) / "claims.xlsx")
            workbook = load_workbook(path)
            claims = workbook["Claims"]
            summary = workbook["Summary"]
            self.assertEqual(claims.freeze_panes, "A2")
            self.assertEqual(claims["D2"].value, self.sample().paper_sentence)
            self.assertTrue(claims.data_validations.dataValidation)
            validation = claims.data_validations.dataValidation[0]
            self.assertIn("consistent", validation.formula1)
            self.assertEqual(summary["B2"].value, '=COUNTIF(Claims!$K:$K,A2)')
            self.assertEqual(summary["B7"].value, '=COUNTIF(Claims!$K:$K,A7)')


if __name__ == "__main__":
    unittest.main()
