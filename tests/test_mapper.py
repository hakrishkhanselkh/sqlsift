"""Tests for sqlsift.mapper."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.mapper import cast_column, map_rows, rename_key


def _added(key, row):
    return RowDiff(kind="added", key=key, row=row, delta=None)


def _removed(key, row):
    return RowDiff(kind="removed", key=key, row=row, delta=None)


def _modified(key, row, delta):
    return RowDiff(kind="modified", key=key, row=row, delta=delta)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# map_rows
# ---------------------------------------------------------------------------

def test_map_rows_empty_result():
    result = _make_result()
    out = map_rows(result, {"price": lambda v: v * 2})
    assert out.diffs == []


def test_map_rows_transforms_added_row():
    result = _make_result(_added((1,), {"id": 1, "price": 10}))
    out = map_rows(result, {"price": lambda v: v * 2})
    assert out.diffs[0].row["price"] == 20


def test_map_rows_transforms_removed_row():
    result = _make_result(_removed((2,), {"id": 2, "price": 5}))
    out = map_rows(result, {"price": lambda v: v + 1})
    assert out.diffs[0].row["price"] == 6


def test_map_rows_transforms_modified_row_and_delta():
    diff = _modified(
        (3,),
        {"id": 3, "price": 100},
        {"price": (100, 200)},
    )
    out = map_rows(_make_result(diff), {"price": lambda v: v / 100})
    assert out.diffs[0].row["price"] == pytest.approx(1.0)
    before, after = out.diffs[0].delta["price"]
    assert before == pytest.approx(1.0)
    assert after == pytest.approx(2.0)


def test_map_rows_ignores_missing_columns():
    result = _make_result(_added((1,), {"id": 1, "name": "alice"}))
    out = map_rows(result, {"price": lambda v: v * 2})
    assert out.diffs[0].row == {"id": 1, "name": "alice"}


def test_map_rows_does_not_mutate_original():
    original = {"id": 1, "score": 5}
    result = _make_result(_added((1,), original))
    map_rows(result, {"score": lambda v: v * 10})
    assert original["score"] == 5


# ---------------------------------------------------------------------------
# rename_key
# ---------------------------------------------------------------------------

def test_rename_key_renames_in_row():
    result = _make_result(_added((1,), {"id": 1, "amt": 42}))
    out = rename_key(result, "amt", "amount")
    assert "amount" in out.diffs[0].row
    assert "amt" not in out.diffs[0].row


def test_rename_key_renames_in_delta():
    diff = _modified((1,), {"id": 1, "amt": 10}, {"amt": (10, 20)})
    out = rename_key(_make_result(diff), "amt", "amount")
    assert "amount" in out.diffs[0].delta
    assert "amt" not in out.diffs[0].delta


def test_rename_key_missing_column_is_noop():
    result = _make_result(_added((1,), {"id": 1, "val": 9}))
    out = rename_key(result, "nonexistent", "x")
    assert out.diffs[0].row == {"id": 1, "val": 9}


# ---------------------------------------------------------------------------
# cast_column
# ---------------------------------------------------------------------------

def test_cast_column_converts_string_to_int():
    result = _make_result(_added((1,), {"id": 1, "qty": "7"}))
    out = cast_column(result, "qty", int)
    assert out.diffs[0].row["qty"] == 7
    assert isinstance(out.diffs[0].row["qty"], int)


def test_cast_column_none_stays_none():
    result = _make_result(_added((1,), {"id": 1, "qty": None}))
    out = cast_column(result, "qty", int)
    assert out.diffs[0].row["qty"] is None
