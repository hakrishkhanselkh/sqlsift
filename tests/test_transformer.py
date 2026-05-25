"""Tests for sqlsift.transformer."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.transformer import drop_columns, rename_columns, transform_rows


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _added(key, row):
    return RowDiff(kind="added", key=key, row=row, delta=None)


def _removed(key, row):
    return RowDiff(kind="removed", key=key, row=row, delta=None)


def _modified(key, row, delta):
    return RowDiff(kind="modified", key=key, row=row, delta=delta)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# transform_rows
# ---------------------------------------------------------------------------

def test_transform_rows_empty_result():
    result = transform_rows(_make_result(), {"price": float})
    assert result.diffs == []


def test_transform_rows_modifies_row_values():
    rd = _added((1,), {"id": 1, "name": "  alice  "})
    result = transform_rows(_make_result(rd), {"name": str.strip})
    assert result.diffs[0].row["name"] == "alice"


def test_transform_rows_leaves_other_columns_unchanged():
    rd = _added((1,), {"id": 1, "name": "bob"})
    result = transform_rows(_make_result(rd), {"name": str.upper})
    assert result.diffs[0].row["id"] == 1


def test_transform_rows_applies_to_delta_old_and_new():
    rd = _modified(
        (1,),
        {"id": 1, "score": 10},
        {"score": ("5", "10")},
    )
    result = transform_rows(_make_result(rd), {"score": int})
    assert result.diffs[0].delta["score"] == (5, 10)


def test_transform_rows_ignores_missing_columns():
    rd = _added((1,), {"id": 1})
    result = transform_rows(_make_result(rd), {"nonexistent": str.upper})
    assert result.diffs[0].row == {"id": 1}


def test_transform_rows_does_not_mutate_original():
    rd = _added((1,), {"id": 1, "val": "x"})
    original = _make_result(rd)
    transform_rows(original, {"val": str.upper})
    assert original.diffs[0].row["val"] == "x"


# ---------------------------------------------------------------------------
# rename_columns
# ---------------------------------------------------------------------------

def test_rename_columns_renames_row_key():
    rd = _added((1,), {"old_name": "alice", "id": 1})
    result = rename_columns(_make_result(rd), {"old_name": "name"})
    assert "name" in result.diffs[0].row
    assert "old_name" not in result.diffs[0].row


def test_rename_columns_renames_delta_key():
    rd = _modified((1,), {"id": 1, "old_col": 2}, {"old_col": (1, 2)})
    result = rename_columns(_make_result(rd), {"old_col": "new_col"})
    assert "new_col" in result.diffs[0].delta
    assert "old_col" not in result.diffs[0].delta


def test_rename_columns_unknown_column_unchanged():
    rd = _added((1,), {"id": 1})
    result = rename_columns(_make_result(rd), {"missing": "other"})
    assert result.diffs[0].row == {"id": 1}


# ---------------------------------------------------------------------------
# drop_columns
# ---------------------------------------------------------------------------

def test_drop_columns_removes_from_row():
    rd = _added((1,), {"id": 1, "secret": "x", "name": "bob"})
    result = drop_columns(_make_result(rd), ["secret"])
    assert "secret" not in result.diffs[0].row
    assert "name" in result.diffs[0].row


def test_drop_columns_removes_from_delta():
    rd = _modified((1,), {"id": 1, "a": 2, "b": 3}, {"a": (1, 2), "b": (2, 3)})
    result = drop_columns(_make_result(rd), ["b"])
    assert "b" not in result.diffs[0].delta
    assert "a" in result.diffs[0].delta


def test_drop_columns_empty_drop_list():
    rd = _added((1,), {"id": 1, "val": 9})
    result = drop_columns(_make_result(rd), [])
    assert result.diffs[0].row == {"id": 1, "val": 9}


def test_drop_columns_does_not_mutate_original():
    rd = _added((1,), {"id": 1, "val": 9})
    original = _make_result(rd)
    drop_columns(original, ["val"])
    assert "val" in original.diffs[0].row
