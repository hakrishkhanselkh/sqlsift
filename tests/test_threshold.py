"""Tests for sqlsift.threshold."""
from __future__ import annotations

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.threshold import by_absolute_change, by_relative_change, above_value


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _added(key, row):
    return RowDiff(key=key, kind="added", before=None, after=row, delta=None)


def _removed(key, row):
    return RowDiff(key=key, kind="removed", before=row, after=None, delta=None)


def _modified(key, before, after, delta):
    return RowDiff(key=key, kind="modified", before=before, after=after, delta=delta)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# by_absolute_change
# ---------------------------------------------------------------------------

def test_by_absolute_change_keeps_large_changes():
    r1 = _modified((1,), {"id": 1, "v": 10}, {"id": 1, "v": 60},
                   {"v": {"before": 10, "after": 60}})
    r2 = _modified((2,), {"id": 2, "v": 10}, {"id": 2, "v": 12},
                   {"v": {"before": 10, "after": 12}})
    result = _make_result(r1, r2)
    filtered = by_absolute_change(result, "v", min_change=40)
    keys = [d.key for d in filtered.diffs]
    assert (1,) in keys
    assert (2,) not in keys


def test_by_absolute_change_passes_non_modified_through():
    added = _added((3,), {"id": 3, "v": 5})
    removed = _removed((4,), {"id": 4, "v": 5})
    result = _make_result(added, removed)
    filtered = by_absolute_change(result, "v", min_change=1)
    assert len(filtered.diffs) == 2


def test_by_absolute_change_empty_result():
    assert by_absolute_change(_make_result(), "v", 10).diffs == []


# ---------------------------------------------------------------------------
# by_relative_change
# ---------------------------------------------------------------------------

def test_by_relative_change_keeps_large_ratio():
    r1 = _modified((1,), {"id": 1, "price": 100}, {"id": 1, "price": 200},
                   {"price": {"before": 100, "after": 200}})
    r2 = _modified((2,), {"id": 2, "price": 100}, {"id": 2, "price": 101},
                   {"price": {"before": 100, "after": 101}})
    result = _make_result(r1, r2)
    filtered = by_relative_change(result, "price", min_ratio=0.5)
    keys = [d.key for d in filtered.diffs]
    assert (1,) in keys
    assert (2,) not in keys


def test_by_relative_change_skips_zero_before():
    row = _modified((1,), {"id": 1, "v": 0}, {"id": 1, "v": 10},
                    {"v": {"before": 0, "after": 10}})
    result = _make_result(row)
    filtered = by_relative_change(result, "v", min_ratio=0.1)
    assert filtered.diffs == []


def test_by_relative_change_non_numeric_skipped():
    row = _modified((1,), {"id": 1, "tag": "a"}, {"id": 1, "tag": "b"},
                    {"tag": {"before": "a", "after": "b"}})
    result = _make_result(row)
    filtered = by_relative_change(result, "tag", min_ratio=0.1)
    assert filtered.diffs == []


# ---------------------------------------------------------------------------
# above_value
# ---------------------------------------------------------------------------

def test_above_value_filters_added_rows():
    r1 = _added((1,), {"id": 1, "score": 95})
    r2 = _added((2,), {"id": 2, "score": 40})
    result = _make_result(r1, r2)
    filtered = above_value(result, "score", threshold=50)
    keys = [d.key for d in filtered.diffs]
    assert (1,) in keys
    assert (2,) not in keys


def test_above_value_passes_removed_through():
    removed = _removed((5,), {"id": 5, "score": 10})
    result = _make_result(removed)
    filtered = above_value(result, "score", threshold=50)
    assert len(filtered.diffs) == 1


def test_above_value_modified_uses_after_value():
    row = _modified((1,), {"id": 1, "v": 10}, {"id": 1, "v": 80},
                    {"v": {"before": 10, "after": 80}})
    result = _make_result(row)
    filtered = above_value(result, "v", threshold=50)
    assert len(filtered.diffs) == 1
