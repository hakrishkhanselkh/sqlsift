"""Tests for sqlsift.truncator."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.truncator import by_count, by_fraction, drop_beyond


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _added(key: str) -> RowDiff:
    return RowDiff(kind="added", key={"id": key}, left=None, right={"id": key, "v": 1})


def _removed(key: str) -> RowDiff:
    return RowDiff(kind="removed", key={"id": key}, left={"id": key, "v": 0}, right=None)


def _modified(key: str) -> RowDiff:
    return RowDiff(
        kind="modified",
        key={"id": key},
        left={"id": key, "v": 0},
        right={"id": key, "v": 1},
        delta={"v": (0, 1)},
    )


def _make_result(*diffs: RowDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs), key_columns=["id"])


# ---------------------------------------------------------------------------
# by_count
# ---------------------------------------------------------------------------

def test_by_count_empty_result():
    result = _make_result()
    assert len(by_count(result, 5).diffs) == 0


def test_by_count_limits_all_kinds():
    result = _make_result(_added("a"), _added("b"), _removed("c"), _modified("d"))
    truncated = by_count(result, 2)
    assert len(truncated.diffs) == 2


def test_by_count_zero_returns_empty():
    result = _make_result(_added("a"), _removed("b"))
    assert by_count(result, 0).diffs == []


def test_by_count_larger_than_set_returns_all():
    result = _make_result(_added("a"), _removed("b"))
    assert len(by_count(result, 100).diffs) == 2


def test_by_count_with_kind_only_limits_that_kind():
    result = _make_result(_added("a"), _added("b"), _removed("c"), _removed("d"))
    truncated = by_count(result, 1, kind="added")
    kinds = [r.kind for r in truncated.diffs]
    assert kinds.count("added") == 1
    assert kinds.count("removed") == 2


def test_by_count_negative_raises():
    result = _make_result(_added("a"))
    with pytest.raises(ValueError, match="non-negative"):
        by_count(result, -1)


def test_by_count_invalid_kind_raises():
    result = _make_result(_added("a"))
    with pytest.raises(ValueError, match="kind"):
        by_count(result, 1, kind="unknown")


# ---------------------------------------------------------------------------
# by_fraction
# ---------------------------------------------------------------------------

def test_by_fraction_half():
    result = _make_result(_added("a"), _added("b"), _added("c"), _added("d"))
    truncated = by_fraction(result, 0.5)
    assert len(truncated.diffs) == 2


def test_by_fraction_zero_returns_empty():
    result = _make_result(_added("a"), _removed("b"))
    assert by_fraction(result, 0.0).diffs == []


def test_by_fraction_one_returns_all():
    result = _make_result(_added("a"), _removed("b"), _modified("c"))
    assert len(by_fraction(result, 1.0).diffs) == 3


def test_by_fraction_out_of_range_raises():
    result = _make_result(_added("a"))
    with pytest.raises(ValueError, match="fraction"):
        by_fraction(result, 1.5)


def test_by_fraction_with_kind():
    result = _make_result(
        _modified("a"), _modified("b"), _modified("c"), _modified("d"),
        _added("e"),
    )
    truncated = by_fraction(result, 0.5, kind="modified")
    assert sum(1 for r in truncated.diffs if r.kind == "modified") == 2
    assert sum(1 for r in truncated.diffs if r.kind == "added") == 1


# ---------------------------------------------------------------------------
# drop_beyond
# ---------------------------------------------------------------------------

def test_drop_beyond_caps_total():
    result = _make_result(_added("a"), _removed("b"), _modified("c"), _added("d"))
    assert len(drop_beyond(result, 3).diffs) == 3


def test_drop_beyond_preserves_key_columns():
    result = _make_result(_added("a"), _added("b"))
    truncated = drop_beyond(result, 1)
    assert truncated.key_columns == ["id"]
