"""Data structures for RPaperCodeAudit exports."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from typing import Any, Iterable


SCHEMA_FIELDS = (
    "id",
    "package",
    "commit_hash",
    "paper_sentence",
    "paper_section",
    "claim_type",
    "expected_implementation",
    "code_file",
    "code_lines",
    "code_excerpt",
    "verdict",
    "issue_category",
    "tests_found",
    "documentation_found",
    "checked_by_me",
    "notes",
    "llm_model",
    "prompt_version",
    "timestamp",
)

VERDICTS = ("consistent", "partial", "inconsistent", "not found", "not verified")


@dataclass(slots=True)
class ClaimRecord:
    """One auditable paper claim and its human-review state."""

    id: str
    package: str = ""
    commit_hash: str = ""
    paper_sentence: str = ""
    paper_section: str = ""
    claim_type: str = ""
    expected_implementation: str = ""
    code_file: str = ""
    code_lines: str = ""
    code_excerpt: str = ""
    verdict: str = "not verified"
    issue_category: str = ""
    tests_found: str = ""
    documentation_found: str = ""
    checked_by_me: bool = False
    notes: str = ""
    llm_model: str = ""
    prompt_version: str = ""
    timestamp: str = ""

    def to_row(self) -> dict[str, Any]:
        """Return a dict in the stable export-column order."""
        row = asdict(self)
        return {name: row[name] for name in SCHEMA_FIELDS}


def records_to_rows(records: Iterable[ClaimRecord]) -> list[dict[str, Any]]:
    """Convert records to export rows while preserving schema order."""
    return [record.to_row() for record in records]


def validate_schema() -> None:
    """Fail fast if the dataclass and export schema drift apart."""
    dataclass_fields = tuple(field.name for field in fields(ClaimRecord))
    if dataclass_fields != SCHEMA_FIELDS:
        raise RuntimeError(
            "ClaimRecord fields do not match SCHEMA_FIELDS: "
            f"{dataclass_fields!r} != {SCHEMA_FIELDS!r}"
        )


validate_schema()
