"""Tests for sqlsift.joiner."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.joiner import inner, left_only, outer, right_only


def _added(row: dict) -> RowDiff:
    return RowDiff(kind="added", row=row, delta=None)


def _removed(row: dict) -> RowDiff:
    return RowDiff(kind="removed", row=row, delta=None)


def _modified(row: dict, delta: dict) -> RowDiff:
    return RowDiff(kind="modified", row=row, delta=delta)


def _make_result(*diffs: RowDiff) -> DiffResult:
    return DiffResult(list(diffs))


# ---------------------------------------------------------------------------
# inner
# ---------------------------------------------------------------------------

def test_inner_empty_results_returns_empty():
    result = inner(_make_result(), _make_result(), keys=["id"])
    assert result.diffs == []


def test_inner_no_overlap_returns_empty():
    left = _make_result(_added({"id": 1, "v": "a"}))
    right = _make_result(_added({"id": 2, "v": "b"}))
    result = inner(left, right, keys=["id"])
    assert result.diffs == []


def test_inner_full_overlap_returns_all_left():
    left = _make_result(
        _added({"id": 1, "v": "a"}),
        _added({"id": 2, "v": "b"}),
    )
    right = _make_result(
        _removed({"id": 1, "v": "x"}),
        _removed({"id": 2, "v": "y"}),
    )
    result = inner(left, right, keys=["id"])
    assert len(result.diffs) == 2


def test_inner_partial_overlap():
    left = _make_result(
        _added({"id": 1}),
        _added({"id": 2}),
        _added({"id": 3}),
    )
    right = _make_result(_removed({"id": 2}), _removed({"id": 3}))
    result = inner(left, right, keys=["id"])
    ids = [rd.row["id"] for rd in result.diffs]
    assert sorted(ids) == [2, 3]


def test_inner_composite_key():
    left = _make_result(
        _added({"a": 1, "b": "x"}),
        _added({"a": 1, "b": "y"}),
    )
    right = _make_result(_removed({"a": 1, "b": "x"}))
    result = inner(left, right, keys=["a", "b"])
    assert len(result.diffs) == 1
    assert result.diffs[0].row["b"] == "x"


# ---------------------------------------------------------------------------
# left_only / right_only
# ---------------------------------------------------------------------------

def test_left_only_returns_unmatched_from_left():
    left = _make_result(_added({"id": 1}), _added({"id": 2}))
    right = _make_result(_removed({"id": 2}))
    result = left_only(left, right, keys=["id"])
    assert len(result.diffs) == 1
    assert result.diffs[0].row["id"] == 1


def test_right_only_returns_unmatched_from_right():
    left = _make_result(_added({"id": 1}))
    right = _make_result(_removed({"id": 1}), _removed({"id": 99}))
    result = right_only(left, right, keys=["id"])
    assert len(result.diffs) == 1
    assert result.diffs[0].row["id"] == 99


# ---------------------------------------------------------------------------
# outer
# ---------------------------------------------------------------------------

def test_outer_returns_three_parts():
    left = _make_result(_added({"id": 1}), _added({"id": 2}))
    right = _make_result(_removed({"id": 2}), _removed({"id": 3}))
    shared, lo, ro = outer(left, right, keys=["id"])
    assert len(shared.diffs) == 1  # id=2
    assert len(lo.diffs) == 1     # id=1
    assert len(ro.diffs) == 1     # id=3


def test_outer_all_shared():
    left = _make_result(_added({"id": 1}))
    right = _make_result(_removed({"id": 1}))
    shared, lo, ro = outer(left, right, keys=["id"])
    assert len(shared.diffs) == 1
    assert lo.diffs == []
    assert ro.diffs == []


def test_outer_no_overlap():
    left = _make_result(_added({"id": 1}))
    right = _make_result(_removed({"id": 2}))
    shared, lo, ro = outer(left, right, keys=["id"])
    assert shared.diffs == []
    assert len(lo.diffs) == 1
    assert len(ro.diffs) == 1
