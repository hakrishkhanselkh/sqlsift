"""Tests for sqlsift.comparator."""
from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.comparator import (
    values_equal,
    column_delta,
    changed_in_column,
    compare_column,
    numeric_drift,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _added(key, row):
    return RowDiff(key=key, kind="added", before=None, after=row, delta=None)


def _removed(key, row):
    return RowDiff(key=key, kind="removed", before=row, after=None, delta=None)


def _modified(key, before, after, delta):
    return RowDiff(key=key, kind="modified", before=before, after=after, delta=delta)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# values_equal
# ---------------------------------------------------------------------------

def test_values_equal_identical():
    assert values_equal(1, 1) is True


def test_values_equal_different():
    assert values_equal(1, 2) is False


def test_values_equal_coerce_string_int():
    assert values_equal("1", 1, coerce=True) is True


def test_values_equal_coerce_disabled():
    assert values_equal("1", 1, coerce=False) is False


def test_values_equal_none():
    assert values_equal(None, None) is True


# ---------------------------------------------------------------------------
# column_delta
# ---------------------------------------------------------------------------

def test_column_delta_returns_before_after():
    row = _modified((1,), {"id": 1, "val": 10}, {"id": 1, "val": 20},
                    {"val": {"before": 10, "after": 20}})
    assert column_delta(row, "val") == {"before": 10, "after": 20}


def test_column_delta_missing_column():
    row = _modified((1,), {"id": 1, "val": 10}, {"id": 1, "val": 20},
                    {"val": {"before": 10, "after": 20}})
    assert column_delta(row, "name") is None


def test_column_delta_non_modified_row():
    row = _added((1,), {"id": 1, "val": 5})
    assert column_delta(row, "val") is None


# ---------------------------------------------------------------------------
# changed_in_column
# ---------------------------------------------------------------------------

def test_changed_in_column_finds_rows():
    r1 = _modified((1,), {"id": 1, "x": 1}, {"id": 1, "x": 2},
                   {"x": {"before": 1, "after": 2}})
    r2 = _modified((2,), {"id": 2, "y": 1}, {"id": 2, "y": 3},
                   {"y": {"before": 1, "after": 3}})
    result = _make_result(r1, r2)
    assert changed_in_column(result, "x") == [r1]


def test_changed_in_column_empty_result():
    assert changed_in_column(_make_result(), "x") == []


def test_changed_in_column_multiple_matches():
    """All modified rows that include the target column are returned."""
    r1 = _modified((1,), {"id": 1, "x": 1}, {"id": 1, "x": 2},
                   {"x": {"before": 1, "after": 2}})
    r2 = _modified((2,), {"id": 2, "x": 5}, {"id": 2, "x": 9},
                   {"x": {"before": 5, "after": 9}})
    r3 = _modified((3,), {"id": 3, "y": 0}, {"id": 3, "y": 1},
                   {"y": {"before": 0, "after": 1}})
    result = _make_result(r1, r2, r3)
    assert changed_in_column(result, "x") == [r1, r2]


# ---------------------------------------------------------------------------
# compare_column
# ---------------------------------------------------------------------------
