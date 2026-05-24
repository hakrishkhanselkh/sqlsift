"""Tests for sqlsift.summarizer."""

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.summarizer import ColumnStats, DiffSummary, summarize


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(
    added=None,
    removed=None,
    modified=None,
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        modified=modified or [],
    )


def _modified(key, diff: dict) -> RowDiff:
    return RowDiff(kind="modified", key=key, left={}, right={}, diff=diff)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_empty_result_produces_zero_counts():
    summary = summarize(_make_result())
    assert summary.added_count == 0
    assert summary.removed_count == 0
    assert summary.modified_count == 0
    assert summary.unchanged_count == 0
    assert not summary.has_differences


def test_added_count():
    row = RowDiff(kind="added", key=(1,), left=None, right={"id": 1}, diff=None)
    summary = summarize(_make_result(added=[row]))
    assert summary.added_count == 1
    assert summary.has_differences


def test_removed_count():
    row = RowDiff(kind="removed", key=(2,), left={"id": 2}, right=None, diff=None)
    summary = summarize(_make_result(removed=[row]))
    assert summary.removed_count == 1
    assert summary.has_differences


def test_modified_count():
    row = _modified(key=(3,), diff={"name": ("old", "new")})
    summary = summarize(_make_result(modified=[row]))
    assert summary.modified_count == 1


def test_unchanged_count_derived_from_total():
    row = RowDiff(kind="added", key=(1,), left=None, right={"id": 1}, diff=None)
    summary = summarize(_make_result(added=[row]), total_rows_compared=10)
    assert summary.unchanged_count == 9
    assert summary.total_rows_compared == 10


def test_unchanged_never_negative():
    rows = [_modified(key=(i,), diff={"x": (i, i + 1)}) for i in range(5)]
    # Provide a total smaller than the diff count — should clamp to 0.
    summary = summarize(_make_result(modified=rows), total_rows_compared=2)
    assert summary.unchanged_count == 0


def test_column_stats_sorted_by_frequency():
    diffs = [
        _modified((1,), {"age": (1, 2), "name": ("a", "b")}),
        _modified((2,), {"age": (3, 4)}),
        _modified((3,), {"age": (5, 6), "email": ("x", "y")}),
    ]
    summary = summarize(_make_result(modified=diffs))
    cols = [cs.column for cs in summary.column_stats]
    # 'age' changed 3 times, should be first
    assert cols[0] == "age"
    assert set(cols) == {"age", "name", "email"}


def test_column_stats_change_count():
    diffs = [
        _modified((1,), {"score": (10, 20)}),
        _modified((2,), {"score": (30, 40)}),
    ]
    summary = summarize(_make_result(modified=diffs))
    assert summary.column_stats[0].column == "score"
    assert summary.column_stats[0].change_count == 2


def test_as_dict_keys():
    summary = summarize(_make_result())
    d = summary.as_dict()
    expected_keys = {
        "total_rows_compared", "added", "removed",
        "modified", "unchanged", "has_differences", "column_stats",
    }
    assert set(d.keys()) == expected_keys


def test_column_stats_as_dict():
    cs = ColumnStats(column="price", change_count=7)
    assert cs.as_dict == {"column": "price", "change_count": 7}
