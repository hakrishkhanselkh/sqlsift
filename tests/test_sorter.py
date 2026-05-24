"""Tests for sqlsift.sorter."""

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.sorter import by_key, by_column, by_kind


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(*diffs: RowDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


def _added(key, row: dict) -> RowDiff:
    return RowDiff(kind="added", key=key, old_row=None, new_row=row)


def _removed(key, row: dict) -> RowDiff:
    return RowDiff(kind="removed", key=key, old_row=row, new_row=None)


def _modified(key, old: dict, new: dict) -> RowDiff:
    return RowDiff(kind="modified", key=key, old_row=old, new_row=new)


# ---------------------------------------------------------------------------
# by_key
# ---------------------------------------------------------------------------

def test_by_key_ascending():
    result = _make_result(
        _added((3,), {"name": "c"}),
        _added((1,), {"name": "a"}),
        _added((2,), {"name": "b"}),
    )
    sorted_result = by_key(result)
    keys = [d.key for d in sorted_result.diffs]
    assert keys == [(1,), (2,), (3,)]


def test_by_key_descending():
    result = _make_result(
        _added((1,), {"name": "a"}),
        _added((3,), {"name": "c"}),
        _added((2,), {"name": "b"}),
    )
    sorted_result = by_key(result, reverse=True)
    keys = [d.key for d in sorted_result.diffs]
    assert keys == [(3,), (2,), (1,)]


def test_by_key_composite():
    result = _make_result(
        _added(("b", 2), {}),
        _added(("a", 10), {}),
        _added(("a", 2), {}),
    )
    sorted_result = by_key(result)
    keys = [d.key for d in sorted_result.diffs]
    assert keys == [("a", 2), ("a", 10), ("b", 2)]


def test_by_key_does_not_mutate_original():
    d1 = _added((2,), {})
    d2 = _added((1,), {})
    result = _make_result(d1, d2)
    by_key(result)
    assert result.diffs[0].key == (2,)


# ---------------------------------------------------------------------------
# by_column
# ---------------------------------------------------------------------------

def test_by_column_ascending():
    result = _make_result(
        _added((3,), {"score": 30}),
        _added((1,), {"score": 10}),
        _added((2,), {"score": 20}),
    )
    sorted_result = by_column(result, "score")
    scores = [d.new_row["score"] for d in sorted_result.diffs]
    assert scores == [10, 20, 30]


def test_by_column_missing_column_sorted_last():
    result = _make_result(
        _added((1,), {"score": 5}),
        _added((2,), {"other": 99}),   # no 'score'
        _added((3,), {"score": 1}),
    )
    sorted_result = by_column(result, "score")
    keys = [d.key for d in sorted_result.diffs]
    assert keys[-1] == (2,)


def test_by_column_uses_old_row_for_removed():
    result = _make_result(
        _removed((1,), {"score": 7}),
    )
    sorted_result = by_column(result, "score")
    assert sorted_result.diffs[0].key == (1,)


# ---------------------------------------------------------------------------
# by_kind
# ---------------------------------------------------------------------------

def test_by_kind_default_order():
    result = _make_result(
        _modified((1,), {"x": 1}, {"x": 2}),
        _removed((2,), {"x": 0}),
        _added((3,), {"x": 3}),
    )
    sorted_result = by_kind(result)
    kinds = [d.kind for d in sorted_result.diffs]
    assert kinds == ["added", "removed", "modified"]


def test_by_kind_custom_order():
    result = _make_result(
        _added((1,), {}),
        _removed((2,), {}),
        _modified((3,), {}, {}),
    )
    sorted_result = by_kind(result, order=["modified", "added", "removed"])
    kinds = [d.kind for d in sorted_result.diffs]
    assert kinds == ["modified", "added", "removed"]
