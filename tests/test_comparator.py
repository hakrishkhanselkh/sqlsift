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


# ---------------------------------------------------------------------------
# compare_column
# ---------------------------------------------------------------------------

def test_compare_column_basic():
    row = _modified((1,), {"id": 1, "score": 5}, {"id": 1, "score": 9},
                    {"score": {"before": 5, "after": 9}})
    result = _make_result(row)
    records = compare_column(result, "score")
    assert len(records) == 1
    assert records[0]["before"] == 5
    assert records[0]["after"] == 9


def test_compare_column_with_predicate():
    r1 = _modified((1,), {"id": 1, "v": 1}, {"id": 1, "v": 10},
                   {"v": {"before": 1, "after": 10}})
    r2 = _modified((2,), {"id": 2, "v": 5}, {"id": 2, "v": 6},
                   {"v": {"before": 5, "after": 6}})
    result = _make_result(r1, r2)
    records = compare_column(result, "v", predicate=lambda b, a: (a - b) > 5)
    assert len(records) == 1
    assert records[0]["key"] == (1,)


# ---------------------------------------------------------------------------
# numeric_drift
# ---------------------------------------------------------------------------

def test_numeric_drift_computes_diff():
    row = _modified((1,), {"id": 1, "amount": 100}, {"id": 1, "amount": 150},
                    {"amount": {"before": 100, "after": 150}})
    result = _make_result(row)
    records = numeric_drift(result, "amount")
    assert len(records) == 1
    assert records[0]["diff"] == pytest.approx(50.0)


def test_numeric_drift_skips_non_numeric():
    row = _modified((1,), {"id": 1, "tag": "a"}, {"id": 1, "tag": "b"},
                    {"tag": {"before": "a", "after": "b"}})
    result = _make_result(row)
    assert numeric_drift(result, "tag") == []
