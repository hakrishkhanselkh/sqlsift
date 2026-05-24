"""Tests for sqlsift.pivot."""
import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.pivot import by_column, change_frequency, most_changed_columns


def _added(row):
    return RowDiff(kind="added", key=tuple(row.values())[:1], row=row, delta=None)


def _removed(row):
    return RowDiff(kind="removed", key=tuple(row.values())[:1], row=row, delta=None)


def _modified(key, row, delta):
    return RowDiff(kind="modified", key=key, row=row, delta=delta)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


def test_by_column_empty():
    result = _make_result()
    assert by_column(result) == {}


def test_by_column_added_row():
    diff = _added({"id": 1, "name": "Alice"})
    out = by_column(_make_result(diff))
    assert out["id"]["added"] == [1]
    assert out["name"]["added"] == ["Alice"]


def test_by_column_removed_row():
    diff = _removed({"id": 2, "name": "Bob"})
    out = by_column(_make_result(diff))
    assert out["id"]["removed"] == [2]
    assert out["name"]["removed"] == ["Bob"]


def test_by_column_modified_row():
    diff = _modified((3,), {"id": 3, "name": "Carol"}, {"name": ("Carol", "Caroline")})
    out = by_column(_make_result(diff))
    assert out["name"]["old"] == ["Carol"]
    assert out["name"]["new"] == ["Caroline"]
    assert "id" not in out


def test_by_column_multiple_modified_same_column():
    d1 = _modified((1,), {"id": 1, "score": 10}, {"score": (10, 20)})
    d2 = _modified((2,), {"id": 2, "score": 30}, {"score": (30, 40)})
    out = by_column(_make_result(d1, d2))
    assert out["score"]["old"] == [10, 30]
    assert out["score"]["new"] == [20, 40]


def test_change_frequency_empty():
    assert change_frequency(_make_result()) == {}


def test_change_frequency_counts():
    d1 = _modified((1,), {"id": 1}, {"a": (1, 2), "b": (3, 4)})
    d2 = _modified((2,), {"id": 2}, {"a": (5, 6)})
    freq = change_frequency(_make_result(d1, d2))
    assert freq["a"] == 2
    assert freq["b"] == 1


def test_most_changed_columns_top_n():
    diffs = [
        _modified((i,), {"id": i}, {"x": (0, 1), "y": (0, 1)}) for i in range(3)
    ] + [
        _modified((i + 10,), {"id": i + 10}, {"x": (0, 1)}) for i in range(5)
    ]
    top = most_changed_columns(_make_result(*diffs), top_n=1)
    assert top == ["x"]


def test_most_changed_columns_respects_top_n():
    d = _modified((1,), {"id": 1}, {"a": (1, 2), "b": (3, 4), "c": (5, 6)})
    top = most_changed_columns(_make_result(d), top_n=2)
    assert len(top) == 2


def test_most_changed_columns_empty_result():
    assert most_changed_columns(_make_result()) == []
