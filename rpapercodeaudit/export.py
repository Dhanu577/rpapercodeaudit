"""CSV/XLSX export for human-reviewed claim records."""

from __future__ import annotations

from copy import copy
from pathlib import Path
from typing import Iterable

import pandas as pd
from openpyxl import load_workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

from .schema import ClaimRecord, SCHEMA_FIELDS, VERDICTS, records_to_rows


SUMMARY_VERDICTS = (*VERDICTS, "unverified")


def _dataframe(records: Iterable[ClaimRecord]) -> pd.DataFrame:
    return pd.DataFrame(records_to_rows(records), columns=SCHEMA_FIELDS)


def export_csv(records: Iterable[ClaimRecord], path: str | Path) -> Path:
    """Write records to CSV and return the resolved output path."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    _dataframe(records).to_csv(output, index=False)
    return output.resolve()


def export_xlsx(records: Iterable[ClaimRecord], path: str | Path) -> Path:
    """Write claims and a formula-driven summary sheet to an XLSX file."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = _dataframe(records)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        frame.to_excel(writer, sheet_name="Claims", index=False)
        summary = pd.DataFrame({"Verdict": SUMMARY_VERDICTS, "Count": [None] * len(SUMMARY_VERDICTS)})
        summary.to_excel(writer, sheet_name="Summary", index=False)

    workbook = load_workbook(output)
    claims = workbook["Claims"]
    summary = workbook["Summary"]

    claims.freeze_panes = "A2"
    claims.auto_filter.ref = claims.dimensions
    claims_header_fill = PatternFill("solid", fgColor="1F4E78")
    for cell in claims[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = claims_header_fill

    # All cells are wrapped so long paper/code text remains readable.
    for row in claims.iter_rows():
        for cell in row:
            alignment = copy(cell.alignment)
            alignment.wrap_text = True
            alignment.vertical = "top"
            cell.alignment = alignment

    verdict_col = SCHEMA_FIELDS.index("verdict") + 1
    verdict_letter = claims.cell(row=1, column=verdict_col).column_letter
    last_row = max(claims.max_row, 2)
    validation = DataValidation(type="list", formula1=f'"{",".join(VERDICTS)}"', allow_blank=False)
    validation.error = "Choose a verdict from the dropdown."
    validation.errorTitle = "Invalid verdict"
    validation.prompt = "Select the current human-review verdict."
    validation.promptTitle = "Verdict"
    claims.add_data_validation(validation)
    validation.add(f"{verdict_letter}2:{verdict_letter}{last_row}")

    # Keep a practical minimum width while allowing long text to wrap.
    widths = {"A": 12, "B": 18, "C": 42, "D": 44, "E": 18, "F": 20, "G": 34, "H": 30, "I": 14, "J": 60, "K": 18, "L": 34, "M": 24, "N": 24, "O": 16, "P": 40, "Q": 24, "R": 16, "S": 24}
    for column, width in widths.items():
        claims.column_dimensions[column].width = width

    summary.freeze_panes = "A2"
    summary["A1"].font = Font(bold=True, color="FFFFFF")
    summary["B1"].font = Font(bold=True, color="FFFFFF")
    summary["A1"].fill = claims_header_fill
    summary["B1"].fill = claims_header_fill
    for row in range(2, 2 + len(SUMMARY_VERDICTS)):
        summary.cell(row=row, column=2).value = f'=COUNTIF(Claims!${verdict_letter}:${verdict_letter},A{row})'
    summary.column_dimensions["A"].width = 24
    summary.column_dimensions["B"].width = 14
    for row in summary.iter_rows():
        for cell in row:
            alignment = copy(cell.alignment)
            alignment.wrap_text = True
            alignment.vertical = "top"
            cell.alignment = alignment

    # Make non-reviewed rows visually obvious without altering their data.
    if claims.max_row >= 2:
        claims.conditional_formatting.add(
            f"{verdict_letter}2:{verdict_letter}{claims.max_row}",
            CellIsRule(operator="equal", formula=['"not verified"'], fill=PatternFill("solid", fgColor="FFF2CC")),
        )

    workbook.save(output)
    return output.resolve()
