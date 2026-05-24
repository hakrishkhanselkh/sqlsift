"""Tests for sqlsift.scorer."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.scorer import DiffScore, score


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _added(key, row):
    return RowDiff(kind="added", key=key, left=None, right=row, delta={})


def _removed(key, row):
    return RowDiff(kind="removed", key=key, left=row, right=None, delta={})


def _modified(key, left, right, delta):
    return RowDiff(kind="modified", key=key, left=left, right=right, delta=delta)


def _make_result(added=(), removed=(), modified=(), identical=()):
    return DiffResult(
        added=list(added),
        removed=list(removed),
        modified=list(modified),
        identical=list(identical),
    )


# ---------------------------------------------------------------------------
# DiffScore properties
# ---------------------------------------------------------------------------

def test_similarity_all_identical():
    s = DiffScore(total_rows=10, identical_rows=10, added_rows=0,
                  removed_rows=0, modified_rows=0)
    assert s.similarity == 1.0
    assert s.divergence == 0.0


def test_similarity_no_identical():
    s = DiffScore(total_rows=4, identical_rows=0, added_rows=2,
                  removed_rows=2, modified_rows=0)
    assert s.similarity == 0.0
    assert s.divergence == 1.0


def test_similarity_empty():
    s = DiffScore(total_rows=0, identical_rows=0, added_rows=0,
                  removed_rows=0, modified_rows=0)
    assert s.similarity == 1.0


def test_as_dict_keys():
    s = DiffScore(total_rows=5, identical_rows=3, added_rows=1,
                  removed_rows=1, modified_rows=0)
    d = s.as_dict()
    assert "similarity" in d
    assert "divergence" in d
    assert "column_change_rate" in d


# ---------------------------------------------------------------------------
# score() function
# ---------------------------------------------------------------------------

def test_score_empty_result():
    result = _make_result()
    s = score(result)
    assert s.total_rows == 0
    assert s.similarity == 1.0


def test_score_only_added():
    result = _make_result(added=[
        _added(("1",), {"id": 1, "name": "alice"}),
        _added(("2",), {"id": 2, "name": "bob"}),
    ])
    s = score(result)
    assert s.added_rows == 2
    assert s.removed_rows == 0
    assert s.modified_rows == 0
    assert s.total_rows == 2
    assert s.similarity == 0.0


def test_score_only_removed():
    result = _make_result(removed=[
        _removed(("1",), {"id": 1}),
    ])
    s = score(result)
    assert s.removed_rows == 1
    assert s.total_rows == 1


def test_score_mixed():
    result = _make_result(
        identical=[_added(("1",), {"id": 1})],  # reuse helper for identical
        modified=[_modified(("2",), {"id": 2, "v": 10}, {"id": 2, "v": 20}, {"v": (10, 20)})],
        added=[_added(("3",), {"id": 3})],
    )
    s = score(result)
    assert s.total_rows == 3
    assert s.identical_rows == 1
    assert pytest.approx(s.similarity) == 1 / 3


def test_score_column_change_rate():
    result = _make_result(modified=[
        _modified(("1",), {"a": 1, "b": 1}, {"a": 2, "b": 1}, {"a": (1, 2)}),
        _modified(("2",), {"a": 3, "b": 5}, {"a": 4, "b": 6}, {"a": (3, 4), "b": (5, 6)}),
    ])
    s = score(result)
    assert s.column_change_rate["a"] == pytest.approx(1.0)
    assert s.column_change_rate["b"] == pytest.approx(0.5)


def test_score_as_dict_roundtrip():
    result = _make_result(added=[_added(("x",), {"id": "x"})])
    d = score(result).as_dict()
    assert isinstance(d["similarity"], float)
    assert isinstance(d["column_change_rate"], dict)
