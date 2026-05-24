"""Tests for sqlsift.merger."""

import pytest
from sqlsift.diff import DiffResult, RowDiff
from sqlsift.merger import merge, conflicts


def _added(key, row):
    return RowDiff(key=key, kind="added", left=None, right=row)


def _removed(key, row):
    return RowDiff(key=key, kind="removed", left=row, right=None)


def _modified(key, left, right):
    delta = {k: (left[k], right[k]) for k in left if left[k] != right.get(k)}
    return RowDiff(key=key, kind="modified", left=left, right=right, delta=delta)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# merge()
# ---------------------------------------------------------------------------

def test_merge_requires_at_least_two_results():
    with pytest.raises(ValueError):
        merge(_make_result())


def test_merge_two_empty_results():
    result = merge(_make_result(), _make_result())
    assert result.diffs == []


def test_merge_combines_distinct_rows():
    r1 = _make_result(_added({"id": 1}, {"id": 1, "v": "a"}))
    r2 = _make_result(_added({"id": 2}, {"id": 2, "v": "b"}))
    result = merge(r1, r2)
    assert len(result.diffs) == 2


def test_merge_deduplicates_identical_rows():
    row = _added({"id": 1}, {"id": 1, "v": "a"})
    r1 = _make_result(row)
    r2 = _make_result(_added({"id": 1}, {"id": 1, "v": "a"}))
    result = merge(r1, r2)
    assert len(result.diffs) == 1


def test_merge_preserves_order_first_occurrence_wins():
    a = _added({"id": 1}, {"id": 1, "v": "first"})
    b = _added({"id": 1}, {"id": 1, "v": "second"})
    result = merge(_make_result(a), _make_result(b))
    assert result.diffs[0].right["v"] == "first"


def test_merge_three_results():
    r1 = _make_result(_added({"id": 1}, {"id": 1}))
    r2 = _make_result(_removed({"id": 2}, {"id": 2}))
    r3 = _make_result(_added({"id": 3}, {"id": 3}))
    result = merge(r1, r2, r3)
    assert len(result.diffs) == 3


def test_merge_same_key_different_kind_both_kept():
    added_row = _added({"id": 1}, {"id": 1, "v": "new"})
    removed_row = _removed({"id": 1}, {"id": 1, "v": "old"})
    result = merge(_make_result(added_row), _make_result(removed_row))
    assert len(result.diffs) == 2


# ---------------------------------------------------------------------------
# conflicts()
# ---------------------------------------------------------------------------

def test_conflicts_empty_result():
    assert conflicts(_make_result()) == []


def test_conflicts_no_conflicts():
    r = _make_result(
        _added({"id": 1}, {"id": 1}),
        _removed({"id": 2}, {"id": 2}),
    )
    assert conflicts(r) == []


def test_conflicts_detects_conflicting_key():
    added_row = _added({"id": 1}, {"id": 1, "v": "new"})
    removed_row = _removed({"id": 1}, {"id": 1, "v": "old"})
    result = merge(_make_result(added_row), _make_result(removed_row))
    found = conflicts(result)
    assert len(found) == 2
    kinds = {r.kind for r in found}
    assert kinds == {"added", "removed"}


def test_conflicts_only_returns_conflicting_rows():
    added_row = _added({"id": 1}, {"id": 1})
    removed_row = _removed({"id": 1}, {"id": 1})
    clean_row = _added({"id": 99}, {"id": 99})
    result = merge(
        _make_result(added_row, clean_row),
        _make_result(removed_row),
    )
    found = conflicts(result)
    ids = [r.key["id"] for r in found]
    assert 99 not in ids
    assert ids.count(1) == 2
