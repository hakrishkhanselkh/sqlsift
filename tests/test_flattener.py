"""Tests for sqlsift.flattener."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.flattener import flatten, flatten_modified_delta


# ---------------------------------------------------------------------------
# helpers
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
# flatten
# ---------------------------------------------------------------------------

def test_flatten_empty_result():
    assert flatten(_make_result()) == []


def test_flatten_added_row_contains_row_data():
    result = _make_result(_added((1,), {"id": 1, "name": "Alice"}))
    flat = flatten(result)
    assert len(flat) == 1
    assert flat[0]["id"] == 1
    assert flat[0]["name"] == "Alice"


def test_flatten_meta_kind_and_key_present():
    result = _make_result(_added((1,), {"id": 1}))
    flat = flatten(result)
    assert flat[0]["__kind__"] == "added"
    assert flat[0]["__key__"] == (1,)


def test_flatten_no_meta_excludes_dunder_keys():
    result = _make_result(_added((1,), {"id": 1}))
    flat = flatten(result, include_meta=False)
    assert "__kind__" not in flat[0]
    assert "__key__" not in flat[0]


def test_flatten_modified_row_includes_delta_keys():
    delta = {"score": (10, 20)}
    result = _make_result(_modified((1,), {"id": 1, "score": 20}, delta))
    flat = flatten(result)
    assert flat[0]["_delta_score_before"] == 10
    assert flat[0]["_delta_score_after"] == 20


def test_flatten_filter_by_kind_added_only():
    result = _make_result(
        _added((1,), {"id": 1}),
        _removed((2,), {"id": 2}),
        _modified((3,), {"id": 3, "v": 9}, {"v": (8, 9)}),
    )
    flat = flatten(result, kinds=["added"])
    assert len(flat) == 1
    assert flat[0]["__kind__"] == "added"


def test_flatten_filter_by_multiple_kinds():
    result = _make_result(
        _added((1,), {"id": 1}),
        _removed((2,), {"id": 2}),
    )
    flat = flatten(result, kinds=["added", "removed"])
    assert len(flat) == 2


def test_flatten_kind_filter_case_insensitive():
    result = _make_result(_added((1,), {"id": 1}))
    flat = flatten(result, kinds=["ADDED"])
    assert len(flat) == 1


def test_flatten_preserves_order_of_diffs():
    """Flattened rows should appear in the same order as the input diffs."""
    result = _make_result(
        _added((1,), {"id": 1}),
        _added((2,), {"id": 2}),
        _added((3,), {"id": 3}),
    )
    flat = flatten(result)
    assert [row["id"] for row in flat] == [1, 2, 3]


# ---------------------------------------------------------------------------
# flatten_modified_delta
# ---------------------------------------------------------------------------

def test_flatten_modified_delta_empty_result():
    assert flatten_modified_delta(_make_result()) == []


def test_flatten_modified_delta_skips_added_and_removed():
    result = _make_result(
