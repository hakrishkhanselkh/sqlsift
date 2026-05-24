"""Tests for sqlsift.highlighter."""
from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.highlighter import (
    changed_columns,
    columns_changed_in_result,
    highlight_result,
    highlight_row,
)


def _added(row, key=("id",)):
    return RowDiff(kind="added", key=tuple(row[k] for k in key), row=row, delta=None)


def _removed(row, key=("id",)):
    return RowDiff(kind="removed", key=tuple(row[k] for k in key), row=row, delta=None)


def _modified(row, delta, key=("id",)):
    return RowDiff(kind="modified", key=tuple(row[k] for k in key), row=row, delta=delta)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


# --- changed_columns ---

def test_changed_columns_modified_returns_diff_keys():
    d = _modified({"id": 1, "name": "b"}, delta={"name": ("a", "b")})
    assert changed_columns(d) == {"name"}


def test_changed_columns_added_returns_all_keys():
    d = _added({"id": 1, "name": "x", "val": 9})
    assert changed_columns(d) == {"id", "name", "val"}


def test_changed_columns_removed_returns_all_keys():
    d = _removed({"id": 2, "status": "ok"})
    assert changed_columns(d) == {"id", "status"}


def test_changed_columns_identical_returns_empty():
    d = RowDiff(kind="identical", key=(3,), row={"id": 3}, delta=None)
    assert changed_columns(d) == set()


# --- highlight_row ---

def test_highlight_row_modified_wraps_changed():
    d = _modified({"id": 1, "score": 10}, delta={"score": (5, 10)})
    result = highlight_row(d)
    assert result["score"] == "**10**"
    assert result["id"] == "1"


def test_highlight_row_custom_marker():
    d = _modified({"id": 1, "x": "new"}, delta={"x": ("old", "new")})
    result = highlight_row(d, marker=">>")
    assert result["x"] == ">>new<<"


def test_highlight_row_custom_marker_symmetry():
    # marker wraps both sides identically
    d = _added({"id": 1, "v": 7})
    result = highlight_row(d, marker="!")
    assert result["v"] == "!7!"


def test_highlight_row_added_all_marked():
    d = _added({"id": 5, "col": "hi"})
    result = highlight_row(d)
    assert result["id"] == "**5**"
    assert result["col"] == "**hi**"


# --- highlight_result ---

def test_highlight_result_excludes_identical_by_default():
    identical = RowDiff(kind="identical", key=(1,), row={"id": 1}, delta=None)
    result = _make_result(identical)
    assert highlight_result(result) == []


def test_highlight_result_includes_modified():
    d = _modified({"id": 2, "v": 99}, delta={"v": (0, 99)})
    out = highlight_result(_make_result(d))
    assert len(out) == 1
    assert out[0]["v"] == "**99**"


def test_highlight_result_custom_kinds():
    added = _added({"id": 1})
    removed = _removed({"id": 2})
    out = highlight_result(_make_result(added, removed), kinds=("removed",))
    assert len(out) == 1


# --- columns_changed_in_result ---

def test_columns_changed_in_result_counts():
    d1 = _modified({"id": 1, "a": 2}, delta={"a": (1, 2)})
    d2 = _modified({"id": 2, "a": 5, "b": 3}, delta={"a": (4, 5), "b": (2, 3)})
    counts = columns_changed_in_result(_make_result(d1, d2))
    assert counts["a"] == 2
    assert counts["b"] == 1


def test_columns_changed_in_result_empty():
    assert columns_changed_in_result(_make_result()) == {}
