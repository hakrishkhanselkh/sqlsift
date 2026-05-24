"""Schema and key validation utilities for DiffResult sets."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from sqlsift.diff import DiffResult, RowDiff


@dataclass
class ValidationIssue:
    """A single validation problem found in a DiffResult."""

    kind: str          # 'missing_key', 'unknown_column', 'type_mismatch'
    message: str
    row_index: int = -1

    def __repr__(self) -> str:  # pragma: no cover
        return f"ValidationIssue(kind={self.kind!r}, message={self.message!r})"


@dataclass
class ValidationReport:
    """Aggregated outcome of validating a DiffResult."""

    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.issues) == 0

    def as_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "issue_count": len(self.issues),
            "issues": [
                {"kind": i.kind, "message": i.message, "row_index": i.row_index}
                for i in self.issues
            ],
        }


def _collect_all_diffs(result: DiffResult) -> List[RowDiff]:
    """Return a flat list of all RowDiff entries across added, removed, and modified."""
    return result.added + result.removed + result.modified


def validate_keys(result: DiffResult, keys: Sequence[str]) -> ValidationReport:
    """Check that every diff row contains all required key columns."""
    report = ValidationReport()
    for idx, diff in enumerate(_collect_all_diffs(result)):
        row = diff.left or diff.right or {}
        for key in keys:
            if key not in row:
                report.issues.append(
                    ValidationIssue(
                        kind="missing_key",
                        message=f"Key column {key!r} missing from row at index {idx}",
                        row_index=idx,
                    )
                )
    return report


def validate_columns(result: DiffResult, expected_columns: Sequence[str]) -> ValidationReport:
    """Check that diff rows do not contain columns outside *expected_columns*."""
    report = ValidationReport()
    expected = set(expected_columns)
    for idx, diff in enumerate(_collect_all_diffs(result)):
        row = diff.left or diff.right or {}
        for col in row:
            if col not in expected:
                report.issues.append(
                    ValidationIssue(
                        kind="unknown_column",
                        message=f"Unexpected column {col!r} found at row index {idx}",
                        row_index=idx,
                    )
                )
    return report


def validate_no_null_keys(result: DiffResult, keys: Sequence[str]) -> ValidationReport:
    """Check that key columns are never None/empty in any diff row."""
    report = ValidationReport()
    for idx, diff in enumerate(_collect_all_diffs(result)):
        row = diff.left or diff.right or {}
        for key in keys:
            if row.get(key) is None or row.get(key) == "":
                report.issues.append(
                    ValidationIssue(
                        kind="null_key",
                        message=f"Key column {key!r} is null or empty at row index {idx}",
                        row_index=idx,
                    )
                )
    return report
