"""Tests for sqlsift.deduplicator."""

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.deduplicator import by_key, by_row, duplicates


def _added(row: dict) -> RowDiff:
    return RowDiff(kind="added", row=row, delta={})


def _removed(row: dict) -> RowDiff:
    return RowDiff(kind="removed", row=row, delta={})


def _modified(row: dict, delta: dict) -> RowDiff:
    return RowDiff(kind="modified", row=row, delta=delta)


def _make_result(*diffs: RowDiff) -> DiffResult:
    return DiffResult(list(diffs))


# ---------------------------------------------------------------------------
# by_key
# ---------------------------------------------------------------------------

def test_by_key_empty_result():
    result = _make_result()
    assert by_key(result, ["id"]).diffs == []


def test_by_key_no_duplicates():
    r = _make_result(
        _added({"id": 1, "val": "a"}),
        _added({"id": 2, "val": "b"}),
    )
    deduped = by_key(r, ["id"])
    assert len(deduped.diffs) == 2


def test_by_key_removes_second_occurrence():
    r = _make_result(
        _added({"id": 1, "val": "a"}),
        _added({"id": 1, "val": "b"}),  # duplicate key
    )
    deduped = by_key(r, ["id"])
    assert len(deduped.diffs) == 1
    assert deduped.diffs[0].row["val"] == "a"  # first kept


def test_by_key_different_kinds_not_deduplicated():
    r = _make_result(
        _added({"id": 1, "val": "a"}),
        _removed({"id": 1, "val": "a"}),
    )
    deduped = by_key(r, ["id"])
    assert len(deduped.diffs) == 2


def test_by_key_composite_key():
    r = _make_result(
        _added({"a": 1, "b": 2, "val": "x"}),
        _added({"a": 1, "b": 2, "val": "y"}),  # duplicate composite key
        _added({"a": 1, "b": 3, "val": "z"}),
    )
    deduped = by_key(r, ["a", "b"])
    assert len(deduped.diffs) == 2


# ---------------------------------------------------------------------------
# by_row
# ---------------------------------------------------------------------------

def test_by_row_empty_result():
    result = _make_result()
    assert by_row(result).diffs == []


def test_by_row_removes_identical_diffs():
    d = _added({"id": 1, "val": "a"})
    r = _make_result(d, _added({"id": 1, "val": "a"}))
    deduped = by_row(r)
    assert len(deduped.diffs) == 1


def test_by_row_keeps_different_values():
    r = _make_result(
        _added({"id": 1, "val": "a"}),
        _added({"id": 1, "val": "b"}),
    )
    deduped = by_row(r)
    assert len(deduped.diffs) == 2


def test_by_row_modified_with_same_delta_deduped():
    r = _make_result(
        _modified({"id": 1}, {"val": ("a", "b")}),
        _modified({"id": 1}, {"val": ("a", "b")}),
    )
    deduped = by_row(r)
    assert len(deduped.diffs) == 1


# ---------------------------------------------------------------------------
# duplicates
# ---------------------------------------------------------------------------

def test_duplicates_empty_result():
    result = _make_result()
    assert duplicates(result).diffs == []


def test_duplicates_returns_only_duplicate_diffs():
    r = _make_result(
        _added({"id": 1, "val": "a"}),
        _added({"id": 1, "val": "a"}),  # duplicate
        _added({"id": 2, "val": "b"}),
    )
    dupes = duplicates(r)
    assert len(dupes.diffs) == 1
    assert dupes.diffs[0].row == {"id": 1, "val": "a"}


def test_duplicates_no_duplicates_returns_empty():
    r = _make_result(
        _added({"id": 1, "val": "a"}),
        _added({"id": 2, "val": "b"}),
    )
    dupes = duplicates(r)
    assert dupes.diffs == []
