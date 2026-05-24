"""Tests for sqlsift.segmenter."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.segmenter import by_column_value, by_predicate, sizes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _added(key: dict, row: dict) -> RowDiff:
    return RowDiff(kind="added", key=key, left=None, right=row)


def _removed(key: dict, row: dict) -> RowDiff:
    return RowDiff(kind="removed", key=key, left=row, right=None)


def _modified(key: dict, left: dict, right: dict) -> RowDiff:
    delta = {k: (left[k], right[k]) for k in right if left.get(k) != right.get(k)}
    return RowDiff(kind="modified", key=key, left=left, right=right, delta=delta)


def _make_result(*diffs: RowDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# by_column_value
# ---------------------------------------------------------------------------

def test_by_column_value_empty_result():
    result = _make_result()
    segs = by_column_value(result, "region")
    assert segs == {}


def test_by_column_value_single_segment():
    r = _make_result(
        _added({"id": 1}, {"id": 1, "region": "us"}),
        _added({"id": 2}, {"id": 2, "region": "us"}),
    )
    segs = by_column_value(r, "region")
    assert set(segs.keys()) == {"us"}
    assert len(segs["us"].diffs) == 2


def test_by_column_value_multiple_segments():
    r = _make_result(
        _added({"id": 1}, {"id": 1, "region": "us"}),
        _added({"id": 2}, {"id": 2, "region": "eu"}),
        _removed({"id": 3}, {"id": 3, "region": "us"}),
    )
    segs = by_column_value(r, "region")
    assert len(segs["us"].diffs) == 2
    assert len(segs["eu"].diffs) == 1


def test_by_column_value_missing_column_goes_to_none():
    r = _make_result(
        _added({"id": 1}, {"id": 1, "region": "us"}),
        _added({"id": 2}, {"id": 2}),  # no 'region'
    )
    segs = by_column_value(r, "region")
    assert None in segs
    assert len(segs[None].diffs) == 1


def test_by_column_value_right_source_for_modified():
    r = _make_result(
        _modified({"id": 1}, {"id": 1, "region": "us"}, {"id": 1, "region": "eu"}),
    )
    segs_left = by_column_value(r, "region", source="left")
    segs_right = by_column_value(r, "region", source="right")
    assert "us" in segs_left
    assert "eu" in segs_right


def test_by_column_value_invalid_source_raises():
    r = _make_result(_added({"id": 1}, {"id": 1}))
    with pytest.raises(ValueError, match="source"):
        by_column_value(r, "id", source="both")


# ---------------------------------------------------------------------------
# by_predicate
# ---------------------------------------------------------------------------

def test_by_predicate_empty_result():
    result = _make_result()
    segs = by_predicate(result, {"big": lambda r: True})
    assert segs["big"].diffs == []


def test_by_predicate_routes_correctly():
    r = _make_result(
        _added({"id": 1}, {"id": 1, "amount": 100}),
        _added({"id": 2}, {"id": 2, "amount": 5}),
        _removed({"id": 3}, {"id": 3, "amount": 50}),
    )
    preds = {
        "high": lambda row: (row.right or row.left or {}).get("amount", 0) >= 50,
        "low": lambda row: (row.right or row.left or {}).get("amount", 0) < 50,
    }
    segs = by_predicate(r, preds, default_segment=None)
    assert len(segs["high"].diffs) == 2
    assert len(segs["low"].diffs) == 1


def test_by_predicate_default_segment_catches_unmatched():
    r = _make_result(
        _added({"id": 1}, {"id": 1, "status": "active"}),
        _added({"id": 2}, {"id": 2, "status": "unknown"}),
    )
    preds = {"active": lambda row: (row.right or {}).get("status") == "active"}
    segs = by_predicate(r, preds, default_segment="other")
    assert len(segs["active"].diffs) == 1
    assert len(segs["other"].diffs) == 1


def test_by_predicate_no_default_discards_unmatched():
    r = _make_result(
        _added({"id": 1}, {"id": 1, "status": "active"}),
        _added({"id": 2}, {"id": 2, "status": "unknown"}),
    )
    preds = {"active": lambda row: (row.right or {}).get("status") == "active"}
    segs = by_predicate(r, preds, default_segment=None)
    assert "other" not in segs
    assert len(segs["active"].diffs) == 1


# ---------------------------------------------------------------------------
# sizes
# ---------------------------------------------------------------------------

def test_sizes_returns_counts():
    r = _make_result(
        _added({"id": 1}, {"id": 1, "region": "us"}),
        _added({"id": 2}, {"id": 2, "region": "eu"}),
        _added({"id": 3}, {"id": 3, "region": "us"}),
    )
    segs = by_column_value(r, "region")
    s = sizes(segs)
    assert s["us"] == 2
    assert s["eu"] == 1
