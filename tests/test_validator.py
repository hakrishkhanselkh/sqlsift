"""Tests for sqlsift.validator."""
import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.validator import (
    ValidationReport,
    validate_columns,
    validate_keys,
    validate_no_null_keys,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_result(
    added=None, removed=None, modified=None
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        modified=modified or [],
    )


def _added(row: dict) -> RowDiff:
    return RowDiff(kind="added", left=None, right=row, delta={})


def _removed(row: dict) -> RowDiff:
    return RowDiff(kind="removed", left=row, right=None, delta={})


def _modified(left: dict, right: dict) -> RowDiff:
    delta = {k: (left.get(k), right.get(k)) for k in right if left.get(k) != right.get(k)}
    return RowDiff(kind="modified", left=left, right=right, delta=delta)


# ---------------------------------------------------------------------------
# ValidationReport
# ---------------------------------------------------------------------------

def test_empty_report_is_valid():
    report = ValidationReport()
    assert report.is_valid is True


def test_report_with_issue_is_invalid():
    from sqlsift.validator import ValidationIssue
    report = ValidationReport(issues=[ValidationIssue(kind="missing_key", message="x")])
    assert report.is_valid is False


def test_as_dict_structure():
    report = ValidationReport()
    d = report.as_dict()
    assert d["is_valid"] is True
    assert d["issue_count"] == 0
    assert d["issues"] == []


# ---------------------------------------------------------------------------
# validate_keys
# ---------------------------------------------------------------------------

def test_validate_keys_passes_when_all_present():
    result = _make_result(added=[_added({"id": 1, "name": "Alice"})])
    report = validate_keys(result, keys=["id"])
    assert report.is_valid


def test_validate_keys_detects_missing_key():
    result = _make_result(added=[_added({"name": "Alice"})])
    report = validate_keys(result, keys=["id"])
    assert not report.is_valid
    assert report.issues[0].kind == "missing_key"
    assert "id" in report.issues[0].message


def test_validate_keys_checks_all_diff_kinds():
    result = _make_result(
        added=[_added({"name": "A"})],
        removed=[_removed({"name": "B"})],
        modified=[_modified({"name": "C"}, {"name": "D"})],
    )
    report = validate_keys(result, keys=["id"])
    assert len(report.issues) == 3


# ---------------------------------------------------------------------------
# validate_columns
# ---------------------------------------------------------------------------

def test_validate_columns_passes_when_all_known():
    result = _make_result(added=[_added({"id": 1, "name": "Alice"})])
    report = validate_columns(result, expected_columns=["id", "name"])
    assert report.is_valid


def test_validate_columns_detects_unexpected_column():
    result = _make_result(added=[_added({"id": 1, "ghost": "value"})])
    report = validate_columns(result, expected_columns=["id", "name"])
    assert not report.is_valid
    assert report.issues[0].kind == "unknown_column"
    assert "ghost" in report.issues[0].message


# ---------------------------------------------------------------------------
# validate_no_null_keys
# ---------------------------------------------------------------------------

def test_no_null_keys_passes_with_values():
    result = _make_result(added=[_added({"id": 1})])
    report = validate_no_null_keys(result, keys=["id"])
    assert report.is_valid


def test_no_null_keys_detects_none_value():
    result = _make_result(added=[_added({"id": None})])
    report = validate_no_null_keys(result, keys=["id"])
    assert not report.is_valid
    assert report.issues[0].kind == "null_key"


def test_no_null_keys_empty_result_is_valid():
    result = _make_result()
    report = validate_no_null_keys(result, keys=["id"])
    assert report.is_valid
