"""Tests for sqlsift.ranker."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift import ranker


def _added(key: tuple, row: dict) -> RowDiff:
    return RowDiff(kind="added", key=key, old_row=None, new_row=row, delta={})


def _removed(key: tuple, row: dict) -> RowDiff:
    return RowDiff(kind="removed", key=key, old_row=row, new_row=None, delta={})


def _modified(key: tuple, old: dict, new: dict) -> RowDiff:
    delta = {k: (old.get(k), new.get(k)) for k in new if old.get(k) != new.get(k)}
    return RowDiff(kind="modified", key=key, old_row=old, new_row=new, delta=delta)


def _make_result(*diffs: RowDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# by_column
# ---------------------------------------------------------------------------

def test_by_column_empty_result():
    result = _make_result()
    assert ranker.by_column(result, "amount") == []


def test_by_column_modified_uses_abs_delta():
    rd_small = _modified((1,), {"amount": 100}, {"amount": 105})
    rd_large = _modified((2,), {"amount": 100}, {"amount": 200})
    result = _make_result(rd_small, rd_large)
    ranked = ranker.by_column(result, "amount")
    assert ranked[0] is rd_large
    assert ranked[1] is rd_small


def test_by_column_ascending():
    rd_small = _modified((1,), {"amount": 10}, {"amount": 11})
    rd_large = _modified((2,), {"amount": 10}, {"amount": 99})
    result = _make_result(rd_large, rd_small)
    ranked = ranker.by_column(result, "amount", ascending=True)
    assert ranked[0] is rd_small


def test_by_column_added_uses_new_value():
    rd = _added((3,), {"amount": 42})
    result = _make_result(rd)
    ranked = ranker.by_column(result, "amount")
    assert ranked == [rd]


def test_by_column_removed_uses_old_value():
    rd = _removed((4,), {"amount": 7})
    result = _make_result(rd)
    ranked = ranker.by_column(result, "amount")
    assert ranked == [rd]


def test_by_column_limit():
    diffs = [_modified((i,), {"v": i}, {"v": i * 2}) for i in range(1, 6)]
    result = _make_result(*diffs)
    ranked = ranker.by_column(result, "v", limit=3)
    assert len(ranked) == 3


def test_by_column_missing_column_defaults_to_zero():
    rd = _modified((1,), {"x": 1}, {"x": 2})
    result = _make_result(rd)
    ranked = ranker.by_column(result, "nonexistent")
    assert ranked == [rd]


# ---------------------------------------------------------------------------
# by_score
# ---------------------------------------------------------------------------

def test_by_score_custom_fn():
    rd_a = _added((1,), {"val": 3})
    rd_b = _added((2,), {"val": 9})
    result = _make_result(rd_a, rd_b)
    ranked = ranker.by_score(result, lambda rd: rd.new_row["val"])
    assert ranked[0] is rd_b


def test_by_score_limit():
    diffs = [_added((i,), {"val": i}) for i in range(10)]
    result = _make_result(*diffs)
    ranked = ranker.by_score(result, lambda rd: rd.new_row["val"], limit=4)
    assert len(ranked) == 4


# ---------------------------------------------------------------------------
# top_n / bottom_n
# ---------------------------------------------------------------------------

def test_top_n_returns_highest():
    diffs = [_modified((i,), {"score": 0}, {"score": i}) for i in range(1, 11)]
    result = _make_result(*diffs)
    top = ranker.top_n(result, "score", n=3)
    assert len(top) == 3
    scores = [rd.new_row["score"] for rd in top]
    assert scores == sorted(scores, reverse=True)


def test_bottom_n_returns_lowest():
    diffs = [_modified((i,), {"score": 0}, {"score": i}) for i in range(1, 11)]
    result = _make_result(*diffs)
    bottom = ranker.bottom_n(result, "score", n=3)
    assert len(bottom) == 3
    scores = [rd.new_row["score"] for rd in bottom]
    assert scores == sorted(scores)
