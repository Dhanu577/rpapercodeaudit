#!/usr/bin/env python3
"""Migrate the DESeq2 audit workbook to an orthogonal verdict taxonomy.

The migration keeps the historical verdict fields and adds separate fields for:

* evidence status: what the cited excerpt establishes;
* implementation correctness: what can be concluded about the full implementation;
* review status: who reviewed the row;
* citation quality and validation: whether the citation is mechanically sound.

The script is deliberately conservative. A valid but narrow citation does not
become an implementation contradiction merely because it cannot establish the
whole paper claim.

Typical use from the repository root::

    python migrate_taxonomy.py \
        examples/deseq2/final/deseq2_final_table.xlsx \
        --output examples/deseq2/final/deseq2_taxonomy_v2.xlsx \
        --repo examples/deseq2/repo \
        --paper examples/deseq2/DESeq.txt \
        --commit 76c5f8523716804dbe0a9500b4b7e216c6af225c \
        --report examples/deseq2/final/taxonomy_validation.json

The source repository is read only; package code is never executed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


SCHEMA_VERSION = "2.0"

EVIDENCE_STATUSES = {
    "direct",
    "supporting",
    "insufficient",
    "contradictory",
    "absent",
    "invalid",
}
IMPLEMENTATION_CORRECTNESS = {
    "consistent",
    "partially_consistent",
    "inconsistent",
    "not_determined",
    "not_applicable",
}
REVIEW_STATUSES = {
    "human_reviewed",
    "ai_assisted",
    "independently_reproduced",
    "unreviewed",
}
CITATION_QUALITIES = {
    "exact",
    "valid_but_narrow",
    "valid_but_indirect",
    "invalid",
}
CITATION_VALIDATIONS = {"passed", "failed", "not_checked"}

# These are the 24 retained DESeq2 rows in v0.1.3. The manifest is explicit so
# a missing or unexpected row fails closed instead of receiving a silent default.
# The mapping is intentionally conservative: partial or insufficient evidence
# does not establish a wrong implementation.
DESEQ2_MIGRATION: dict[int, dict[str, str]] = {
    2: {"evidence_status": "insufficient", "implementation_correctness": "not_determined", "citation_quality": "valid_but_narrow", "basis": "comments_only"},
    4: {"evidence_status": "direct", "implementation_correctness": "consistent", "citation_quality": "exact", "basis": "zero_centred_prior_in_log_posterior"},
    6: {"evidence_status": "insufficient", "implementation_correctness": "not_determined", "citation_quality": "valid_but_narrow", "basis": "MLE_beta_extraction_only"},
    10: {"evidence_status": "insufficient", "implementation_correctness": "not_determined", "citation_quality": "valid_but_narrow", "basis": "comment_and_zero_variance_check"},
    12: {"evidence_status": "supporting", "implementation_correctness": "not_determined", "citation_quality": "valid_but_indirect", "basis": "sandwich_covariance_and_contrast_quantities"},
    14: {"evidence_status": "insufficient", "implementation_correctness": "not_determined", "citation_quality": "valid_but_narrow", "basis": "comments_only"},
    16: {"evidence_status": "supporting", "implementation_correctness": "not_determined", "citation_quality": "valid_but_indirect", "basis": "negative_binomial_working_weights"},
    18: {"evidence_status": "supporting", "implementation_correctness": "not_determined", "citation_quality": "valid_but_indirect", "basis": "negative_binomial_working_weights"},
    20: {"evidence_status": "supporting", "implementation_correctness": "not_determined", "citation_quality": "valid_but_indirect", "basis": "weights_not_degrees_of_freedom"},
    21: {"evidence_status": "supporting", "implementation_correctness": "not_determined", "citation_quality": "valid_but_narrow", "basis": "median_default_in_function_signature"},
    25: {"evidence_status": "insufficient", "implementation_correctness": "not_determined", "citation_quality": "valid_but_narrow", "basis": "iteration_setup_without_MLE_call"},
    27: {"evidence_status": "insufficient", "implementation_correctness": "not_determined", "citation_quality": "valid_but_narrow", "basis": "function_signature_only"},
    28: {"evidence_status": "supporting", "implementation_correctness": "not_determined", "citation_quality": "valid_but_indirect", "basis": "zero_centred_prior_in_posterior"},
    29: {"evidence_status": "direct", "implementation_correctness": "consistent", "citation_quality": "exact", "basis": "trigamma_prior_variance_rule"},
    30: {"evidence_status": "insufficient", "implementation_correctness": "not_determined", "citation_quality": "valid_but_narrow", "basis": "generic_weight_excerpt"},
    33: {"evidence_status": "supporting", "implementation_correctness": "not_determined", "citation_quality": "valid_but_indirect", "basis": "outlier_detection_without_MAP_replacement"},
    35: {"evidence_status": "insufficient", "implementation_correctness": "not_determined", "citation_quality": "valid_but_narrow", "basis": "degrees_of_freedom_comment_only"},
    39: {"evidence_status": "direct", "implementation_correctness": "consistent", "citation_quality": "exact", "basis": "squared_MAD_residual_variance"},
    41: {"evidence_status": "insufficient", "implementation_correctness": "not_determined", "citation_quality": "valid_but_narrow", "basis": "comments_only"},
    43: {"evidence_status": "supporting", "implementation_correctness": "not_determined", "citation_quality": "valid_but_narrow", "basis": "outlierSD_default_only"},
    49: {"evidence_status": "supporting", "implementation_correctness": "not_determined", "citation_quality": "valid_but_indirect", "basis": "m_and_p_before_residual_df"},
    51: {"evidence_status": "insufficient", "implementation_correctness": "not_determined", "citation_quality": "valid_but_narrow", "basis": "dispersion_prior_code_not_LFC_convergence"},
    57: {"evidence_status": "supporting", "implementation_correctness": "not_determined", "citation_quality": "valid_but_indirect", "basis": "prior_variance_without_second_fit"},
    61: {"evidence_status": "supporting", "implementation_correctness": "not_determined", "citation_quality": "valid_but_indirect", "basis": "fit_sd_reported_as_lfcSE"},
}

REQUIRED_DESEQ2_ROWS = set(DESEQ2_MIGRATION)


@dataclass
class ValidationIssue:
    row: int | None
    field: str
    message: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class MigrationError(Exception):
    """Raised when the migration cannot safely proceed."""


def normalize_whitespace(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def as_bool_y(value: Any) -> bool:
    return str(value or "").strip().upper() in {"Y", "YES", "TRUE", "1"}


def parse_line_range(value: Any) -> tuple[int, int] | None:
    match = re.fullmatch(r"\s*(\d+)\s*[-–—]\s*(\d+)\s*", str(value or ""))
    if not match:
        return None
    start, end = int(match.group(1)), int(match.group(2))
    return (start, end) if start >= 1 and end >= start else None


def read_exact_excerpt(repo: Path, code_file: str, code_lines: str) -> str:
    parsed = parse_line_range(code_lines)
    if parsed is None:
        raise ValueError(f"invalid line range: {code_lines!r}")
    start, end = parsed
    relative = Path(str(code_file).replace("\\", "/"))
    path = repo / relative
    if not path.is_file():
        raise FileNotFoundError(str(relative))
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    if end > len(lines):
        raise ValueError(f"line range {code_lines!r} exceeds {len(lines)} lines")
    return "".join(lines[start - 1 : end])


def validate_permalink(permalink: Any, code_file: str, code_lines: str, commit: str) -> str | None:
    value = str(permalink or "")
    parsed = parse_line_range(code_lines)
    if not value:
        return "missing GitHub permalink"
    if commit and commit not in value:
        return "permalink does not contain the pinned commit"
    if code_file and str(code_file).replace("\\", "/") not in value:
        return "permalink does not contain the cited file"
    if parsed:
        start, end = parsed
        if f"#L{start}-L{end}" not in value:
            return "permalink does not contain the cited line range"
    return None


def current_column_map(headers: Iterable[Any]) -> dict[str, int]:
    return {str(value): index for index, value in enumerate(headers) if value is not None}


def require_columns(columns: dict[str, int], required: Iterable[str]) -> None:
    missing = [name for name in required if name not in columns]
    if missing:
        raise MigrationError("Input workbook is missing columns: " + ", ".join(missing))


def migration_for_row(row_number: int, legacy_verdict: str) -> dict[str, str]:
    if row_number not in DESEQ2_MIGRATION:
        raise MigrationError(f"No explicit migration manifest entry for retained row {row_number}")
    values = dict(DESEQ2_MIGRATION[row_number])
    values["review_status"] = "human_reviewed"
    values["reviewer_count"] = "1"
    values["legacy_verdict"] = legacy_verdict
    return values


def validate_taxonomy_row(row: dict[str, Any]) -> list[str]:
    """Return cross-field validation errors for one migrated row."""
    errors: list[str] = []
    evidence = row.get("Evidence status", "")
    correctness = row.get("Implementation correctness", "")
    review = row.get("Review status", "")
    citation_quality = row.get("Citation quality", "")
    citation_validation = row.get("Citation validation", "")

    if evidence not in EVIDENCE_STATUSES:
        errors.append(f"invalid Evidence status: {evidence!r}")
    if correctness not in IMPLEMENTATION_CORRECTNESS:
        errors.append(f"invalid Implementation correctness: {correctness!r}")
    if review not in REVIEW_STATUSES:
        errors.append(f"invalid Review status: {review!r}")
    if citation_quality not in CITATION_QUALITIES:
        errors.append(f"invalid Citation quality: {citation_quality!r}")
    if citation_validation not in CITATION_VALIDATIONS:
        errors.append(f"invalid Citation validation: {citation_validation!r}")

    if review == "human_reviewed":
        if not as_bool_y(row.get("Checked by me?")):
            errors.append("human_reviewed requires Checked by me? = Y")
        if not str(row.get("Human check note") or "").strip():
            errors.append("human_reviewed requires Human check note")
        try:
            if int(row.get("Reviewer count") or 0) < 1:
                errors.append("human_reviewed requires Reviewer count >= 1")
        except (TypeError, ValueError):
            errors.append("Reviewer count must be an integer")

    if review == "ai_assisted" and as_bool_y(row.get("Checked by me?")):
        errors.append("ai_assisted cannot have Checked by me? = Y")

    if evidence == "invalid" and citation_quality != "invalid":
        errors.append("invalid evidence requires Citation quality = invalid")
    if evidence in {"absent", "invalid"} and citation_validation == "passed":
        errors.append(f"{evidence} evidence cannot have Citation validation = passed")
    if evidence == "absent" and str(row.get("Code excerpt") or "").strip():
        errors.append("absent evidence cannot have a Code excerpt")
    if correctness == "inconsistent" and evidence != "contradictory":
        errors.append("inconsistent correctness requires contradictory evidence")
    if evidence in {"insufficient", "absent", "invalid"} and correctness == "inconsistent":
        errors.append("insufficient/absent/invalid evidence cannot alone establish inconsistency")
    if citation_quality == "invalid" and evidence != "invalid":
        errors.append("invalid Citation quality requires Evidence status = invalid")
    if citation_validation == "failed" and citation_quality != "invalid":
        errors.append("failed citation validation requires Citation quality = invalid")
    if citation_validation == "passed" and citation_quality == "invalid":
        errors.append("passed citation validation cannot have Citation quality = invalid")
    return errors


def verify_source_row(
    row: dict[str, Any],
    repo: Path | None,
    paper_text: str | None,
    commit: str | None,
) -> tuple[str, list[str]]:
    """Return citation validation status and mechanical validation messages."""
    if repo is None and paper_text is None:
        return "not_checked", []
    errors: list[str] = []
    if paper_text is not None:
        sentence = normalize_whitespace(row.get("Paper sentence"))
        if not sentence or sentence not in normalize_whitespace(paper_text):
            errors.append("paper sentence is not an exact substring after whitespace normalization")
    if repo is not None:
        try:
            actual = read_exact_excerpt(repo, str(row.get("Code file") or ""), str(row.get("Code lines") or ""))
            expected = str(row.get("Code excerpt") or "")
            if actual != expected:
                errors.append("Code excerpt does not exactly match the cited on-disk line range")
        except (OSError, ValueError) as exc:
            errors.append(f"cannot validate code excerpt: {exc}")
    permalink_error = validate_permalink(row.get("GitHub permalink"), str(row.get("Code file") or ""), str(row.get("Code lines") or ""), commit or "")
    if permalink_error:
        errors.append(permalink_error)
    return ("passed" if not errors else "failed"), errors


def git_commit(repo: Path) -> str | None:
    head_file = repo / ".git" / "HEAD"
    # Avoid subprocesses and avoid executing package code. A detached checkout
    # stores the hash directly; a symbolic ref is resolved through the ref file
    # when possible. The CLI can also supply --commit for authoritative checks.
    if not head_file.is_file():
        return None
    head = head_file.read_text(encoding="utf-8").strip()
    if head.startswith("ref: "):
        ref = repo / ".git" / head[5:]
        if ref.is_file():
            return ref.read_text(encoding="utf-8").strip()
        packed = repo / ".git" / "packed-refs"
        if packed.is_file():
            target = head[5:]
            for line in packed.read_text(encoding="utf-8").splitlines():
                if line and not line.startswith("#") and not line.startswith("^"):
                    commit_hash, ref_name = line.split(" ", 1)
                    if ref_name == target:
                        return commit_hash
        return None
    return head


def style_sheet(ws: Any) -> None:
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F4E78")
        cell.alignment = Alignment(wrap_text=True, vertical="top")
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")


def migrate_workbook(
    input_path: Path,
    output_path: Path,
    report_path: Path,
    repo: Path | None = None,
    paper: Path | None = None,
    commit: str | None = None,
    allow_non_deseq2_rows: bool = False,
) -> dict[str, Any]:
    if not input_path.is_file():
        raise MigrationError(f"input workbook not found: {input_path}")
    wb_in = load_workbook(input_path, read_only=True, data_only=False)
    if "Final Table" not in wb_in.sheetnames:
        raise MigrationError("input workbook must contain a 'Final Table' sheet")
    ws_in = wb_in["Final Table"]
    values = list(ws_in.iter_rows(values_only=True))
    if not values:
        raise MigrationError("Final Table is empty")
    columns = current_column_map(values[0])
    require_columns(columns, ["Original row", "Draft verdict", "Verdict", "Paper sentence", "Code file", "Code lines", "Code excerpt", "GitHub permalink", "Checked by me?", "Human check note"])

    source_commit = git_commit(repo) if repo else None
    issues: list[ValidationIssue] = []
    migrated: list[dict[str, Any]] = []
    paper_text = paper.read_text(encoding="utf-8") if paper else None

    source_rows: set[int] = set()
    for raw in values[1:]:
        row = {name: raw[index] if index < len(raw) else None for name, index in columns.items()}
        if row.get("Original row") in (None, ""):
            continue
        try:
            row_number = int(row["Original row"])
        except (TypeError, ValueError):
            issues.append(ValidationIssue(None, "Original row", f"not an integer: {row.get('Original row')!r}"))
            continue
        source_rows.add(row_number)
        legacy_verdict = str(row.get("Verdict") or "").strip().lower()
        try:
            migration = migration_for_row(row_number, legacy_verdict)
        except MigrationError as exc:
            if not allow_non_deseq2_rows:
                issues.append(ValidationIssue(row_number, "migration manifest", str(exc)))
                continue
            migration = {"evidence_status": "absent", "implementation_correctness": "not_determined", "citation_quality": "invalid", "basis": "unmapped_row", "review_status": "unreviewed", "reviewer_count": "0", "legacy_verdict": legacy_verdict}

        output = dict(row)
        # Preserve the old values under explicit legacy names. The original
        # columns are removed below so there is one unambiguous final field.
        output["Legacy draft verdict"] = row.get("Draft verdict") or ""
        output["Legacy verdict"] = row.get("Verdict") or ""
        output.pop("Draft verdict", None)
        output.pop("Verdict", None)
        output["Evidence status"] = migration["evidence_status"]
        output["Implementation correctness"] = migration["implementation_correctness"]
        output["Review status"] = migration["review_status"]
        output["Reviewer count"] = int(migration["reviewer_count"])
        output["Citation quality"] = migration["citation_quality"]
        output["Evidence basis"] = migration["basis"]
        citation_validation, validation_messages = verify_source_row(output, repo, paper_text, commit)
        output["Citation validation"] = citation_validation
        output["Taxonomy schema version"] = SCHEMA_VERSION
        output["Verdict is final"] = "Y"
        if source_commit and commit and source_commit != commit:
            validation_messages.append(f"repository HEAD {source_commit} does not match requested commit {commit}")
            output["Citation validation"] = "failed"
        for message in validation_messages:
            issues.append(ValidationIssue(row_number, "citation", message))
        row_errors = validate_taxonomy_row(output)
        for message in row_errors:
            issues.append(ValidationIssue(row_number, "taxonomy", message))
        migrated.append(output)

    if not allow_non_deseq2_rows:
        missing = REQUIRED_DESEQ2_ROWS - source_rows
        extra = source_rows - REQUIRED_DESEQ2_ROWS
        for row_number in sorted(missing):
            issues.append(ValidationIssue(row_number, "migration manifest", "manifest row is missing from workbook"))
        for row_number in sorted(extra):
            issues.append(ValidationIssue(row_number, "migration manifest", "workbook row is not in the v0.1.3 DESeq2 retained set"))

    # Detect duplicated retained row identifiers.
    if len(source_rows) != len([r for r in migrated if r.get("Original row") not in (None, "")]):
        issues.append(ValidationIssue(None, "Original row", "duplicate retained row identifier"))

    if issues:
        status = "failed"
    else:
        status = "passed"

    # Write an output workbook even on a failed validation only when explicitly
    # requested; by default failure is raised before a potentially misleading
    # deliverable is created.
    if status == "failed":
        report = {
            "schema_version": SCHEMA_VERSION,
            "status": status,
            "input": str(input_path),
            "requested_commit": commit,
            "repository_commit": source_commit,
            "issues": [issue.as_dict() for issue in issues],
            "row_count": len(migrated),
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        raise MigrationError(f"migration validation failed; see {report_path} ({len(issues)} issue(s))")

    # Preserve a copy of the original sheets except Final Table, then add the
    # migrated Final Table and a new Summary. The old workbook's other sheets
    # (for example Dropped Rows) remain available for audit history.
    wb_out = Workbook()
    default = wb_out.active
    wb_out.remove(default)
    for sheet_name in wb_in.sheetnames:
        if sheet_name in {"Final Table", "Summary"}:
            continue
        source_ws = wb_in[sheet_name]
        target_ws = wb_out.create_sheet(sheet_name)
        for source_row in source_ws.iter_rows():
            for cell in source_row:
                target_ws.cell(cell.row, cell.column, cell.value)
        style_sheet(target_ws)

    final_ws = wb_out.create_sheet("Final Table", 0)
    preferred_order = [
        "Original row", "Source table", "Technical component / claim", "Expected implementation",
        "Paper sentence", "Paper sentence (readable)", "Paper section",
        "Legacy draft verdict", "Legacy verdict", "Evidence status", "Implementation correctness",
        "Review status", "Reviewer count", "Citation quality", "Citation validation", "Evidence basis",
        "Disagree with draft?", "Justification", "Issue category", "Code file", "Code lines", "Code excerpt",
        "GitHub permalink", "Vignette Methods-changes note", "Tests / documentation from draft", "Checked by me?",
        "Human check note", "Suggested stronger evidence (unverified by author)", "Verification status", "Notes",
        "Second-review verdict (AI, unconfirmed by author)", "Second-review reason", "Taxonomy schema version", "Verdict is final",
    ]
    all_columns = list(dict.fromkeys(preferred_order + [key for row in migrated for key in row]))
    final_ws.append(all_columns)
    for row in migrated:
        final_ws.append([row.get(column, "") for column in all_columns])
    style_sheet(final_ws)

    col = {name: index + 1 for index, name in enumerate(all_columns)}
    summary = wb_out.create_sheet("Summary")
    summary.append(["Taxonomy v2 summary", "Formula/count"])
    summary.append(["Rows retained", f"=COUNTA('Final Table'!$A:$A)-1"])
    summary.append(["Rows human-checked", f'=COUNTIF(\'Final Table\'!${get_column_letter(col["Checked by me?"])}:${get_column_letter(col["Checked by me?"])},"Y")'])
    summary.append(["Rows AI-assisted only", f'=COUNTIF(\'Final Table\'!${get_column_letter(col["Review status"])}:${get_column_letter(col["Review status"])},"ai_assisted")'])
    summary.append(["Verdicts changed from draft", f'=SUMPRODUCT(--(\'Final Table\'!${get_column_letter(col["Legacy verdict"])}$2:${get_column_letter(col["Legacy verdict"])}${len(migrated)+1}<>\'Final Table\'!${get_column_letter(col["Legacy draft verdict"])}$2:${get_column_letter(col["Legacy draft verdict"])}${len(migrated)+1}))'])
    summary.append([])
    summary.append(["Evidence status", "Count"])
    for value in sorted(EVIDENCE_STATUSES):
        summary.append([value, f'=COUNTIF(\'Final Table\'!${get_column_letter(col["Evidence status"])}:${get_column_letter(col["Evidence status"])},A{summary.max_row + 1})'])
    summary.append([])
    summary.append(["Implementation correctness", "Count"])
    for value in sorted(IMPLEMENTATION_CORRECTNESS):
        summary.append([value, f'=COUNTIF(\'Final Table\'!${get_column_letter(col["Implementation correctness"])}:${get_column_letter(col["Implementation correctness"])},A{summary.max_row + 1})'])
    summary.append([])
    summary.append(["Review status", "Count"])
    for value in sorted(REVIEW_STATUSES):
        summary.append([value, f'=COUNTIF(\'Final Table\'!${get_column_letter(col["Review status"])}:${get_column_letter(col["Review status"])},A{summary.max_row + 1})'])
    summary.append([])
    summary.append(["Citation validation", "Count"])
    for value in sorted(CITATION_VALIDATIONS):
        summary.append([value, f'=COUNTIF(\'Final Table\'!${get_column_letter(col["Citation validation"])}:${get_column_letter(col["Citation validation"])},A{summary.max_row + 1})'])
    summary.append([])
    summary.append(["Legacy verdict", "Count"])
    for value in ("consistent", "partial", "inconsistent", "not found", "not verified"):
        summary.append([value, f'=COUNTIF(\'Final Table\'!${get_column_letter(col["Legacy verdict"])}:${get_column_letter(col["Legacy verdict"])},A{summary.max_row + 1})'])
    style_sheet(summary)
    summary.column_dimensions["A"].width = 34
    summary.column_dimensions["B"].width = 24
    for index in range(1, len(all_columns) + 1):
        final_ws.column_dimensions[get_column_letter(index)].width = min(60, max(14, len(str(all_columns[index - 1])) + 2))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb_out.save(output_path)
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "input": str(input_path),
        "output": str(output_path),
        "requested_commit": commit,
        "repository_commit": source_commit,
        "row_count": len(migrated),
        "counts": {
            "evidence_status": dict(Counter(row["Evidence status"] for row in migrated)),
            "implementation_correctness": dict(Counter(row["Implementation correctness"] for row in migrated)),
            "review_status": dict(Counter(row["Review status"] for row in migrated)),
            "citation_validation": dict(Counter(row["Citation validation"] for row in migrated)),
            "legacy_verdict": dict(Counter(row["Legacy verdict"].strip().lower() for row in migrated)),
        },
        "verdicts_changed_from_draft": sum(str(row["Legacy verdict"]).strip().lower() != str(row["Legacy draft verdict"]).strip().lower() for row in migrated),
        "issues": [],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="existing DESeq2 final-table XLSX")
    parser.add_argument("--output", type=Path, required=True, help="migrated XLSX output path")
    parser.add_argument("--report", type=Path, required=True, help="JSON validation report path")
    parser.add_argument("--repo", type=Path, help="read-only pinned repository checkout for excerpt validation")
    parser.add_argument("--paper", type=Path, help="paper Methods text for exact sentence validation")
    parser.add_argument("--commit", help="expected full repository commit hash")
    parser.add_argument("--allow-non-deseq2-rows", action="store_true", help="allow unmapped rows as unreviewed/absent; not recommended for the DESeq2 release")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = migrate_workbook(
            input_path=args.input,
            output_path=args.output,
            report_path=args.report,
            repo=args.repo,
            paper=args.paper,
            commit=args.commit,
            allow_non_deseq2_rows=args.allow_non_deseq2_rows,
        )
    except MigrationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
