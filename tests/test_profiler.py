"""Tests for sqlsift.profiler."""
from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.profiler import ColumnProfile, profile_column, profile_result


def _added(row):
    return RowDiff(kind="added", key=tuple(row.values())[:1], row=row, delta=None)


def _removed(row):
    return RowDiff(kind="removed", key=tuple(row.values())[:1], row=row, delta=None)


def _modified(row, delta):
    return RowDiff(kind="modified", key=tuple(row.values())[:1], row=row, delta=delta)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# profile_column
# ---------------------------------------------------------------------------

def test_profile_column_total_count():
    result = _make_result(
        _added({"id": 1, "status": "ok"}),
        _added({"id": 2, "status": "fail"}),
        _added({"id": 3, "status": "ok"}),
    )
    p = profile_column(result, "status")
    assert p.total == 3


def test_profile_column_null_count():
    result = _make_result(
        _added({"id": 1, "val": None}),
        _added({"id": 2, "val": 42}),
        _added({"id": 3, "val": None}),
    )
    p = profile_column(result, "val")
    assert p.null_count == 2


def test_profile_column_null_rate():
    result = _make_result(
        _added({"id": 1, "val": None}),
        _added({"id": 2, "val": 10}),
    )
    p = profile_column(result, "val")
    assert p.as_dict()["null_rate"] == 0.5


def test_profile_column_unique_values():
    result = _make_result(
        _added({"id": 1, "c": "a"}),
        _added({"id": 2, "c": "b"}),
        _added({"id": 3, "c": "a"}),
    )
    p = profile_column(result, "c")
    assert p.unique_values == 2


def test_profile_column_top_values_ordering():
    result = _make_result(
        _added({"id": i, "c": "x" if i % 3 != 0 else "y"}) for i in range(9)
    )
    # rebuild without generator (RowDiff not subscriptable)
    rows = [_added({"id": i, "c": "x" if i % 3 != 0 else "y"}) for i in range(9)]
    result = _make_result(*rows)
    p = profile_column(result, "c", top_n=2)
    assert p.top_values[0][0] == "x"  # most frequent first


def test_profile_column_missing_column_returns_zero_total():
    result = _make_result(_added({"id": 1, "a": 1}))
    p = profile_column(result, "nonexistent")
    assert p.total == 0
    assert p.null_count == 0


# ---------------------------------------------------------------------------
# profile_result
# ---------------------------------------------------------------------------

def test_profile_result_empty_returns_empty_dict():
    result = _make_result()
    assert profile_result(result) == {}


def test_profile_result_keys_match_columns():
    result = _make_result(
        _added({"id": 1, "name": "alice", "score": 99}),
    )
    profiles = profile_result(result)
    assert set(profiles.keys()) == {"id", "name", "score"}


def test_profile_result_explicit_columns_subset():
    result = _make_result(
        _added({"id": 1, "name": "alice", "score": 99}),
    )
    profiles = profile_result(result, columns=["name"])
    assert list(profiles.keys()) == ["name"]


def test_profile_result_as_dict_has_required_keys():
    result = _make_result(_added({"id": 1, "v": 5}))
    profiles = profile_result(result)
    d = profiles["v"].as_dict()
    for key in ("column", "total", "null_count", "null_rate", "unique_values", "top_values"):
        assert key in d
