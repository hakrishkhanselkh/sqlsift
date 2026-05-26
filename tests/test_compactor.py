"""Tests for sqlsift.compactor."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.compactor import compact, merge_results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _added(row: dict) -> RowDiff:
    return RowDiff(kind="added", before=None, after=row, delta=None)


def _removed(row: dict) -> RowDiff:
    return RowDiff(kind="removed", before=row, after=None, delta=None)


def _modified(before: dict, after: dict) -> RowDiff:
    delta = {k: (before[k], after[k]) for k in after if before.get(k) != after[k]}
    return RowDiff(kind="modified", before=before, after=after, delta=delta)


def _make_result(*diffs: RowDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# compact()
# ---------------------------------------------------------------------------

def test_compact_empty_result_returns_empty():
    result = _make_result()
    out = compact(result, key_columns=["id"])
    assert out.diffs == []


def test_compact_no_duplicates_returns_all():
    r = _make_result(
        _added({"id": 1, "v": "a"}),
        _added({"id": 2, "v": "b"}),
    )
    out = compact(r, key_columns=["id"])
    assert len(out.diffs) == 2


def test_compact_keep_last_wins():
    first = _added({"id": 1, "v": "first"})
    last = _modified({"id": 1, "v": "first"}, {"id": 1, "v": "last"})
    r = _make_result(first, last)
    out = compact(r, key_columns=["id"], keep="last")
    assert len(out.diffs) == 1
    assert out.diffs[0].kind == "modified"


def test_compact_keep_first_wins():
    first = _added({"id": 1, "v": "first"})
    last = _modified({"id": 1, "v": "first"}, {"id": 1, "v": "last"})
    r = _make_result(first, last)
    out = compact(r, key_columns=["id"], keep="first")
    assert len(out.diffs) == 1
    assert out.diffs[0].kind == "added"


def test_compact_composite_key():
    r = _make_result(
        _added({"a": 1, "b": 1, "v": "x"}),
        _added({"a": 1, "b": 2, "v": "y"}),
        _added({"a": 1, "b": 1, "v": "z"}),  # duplicate of first
    )
    out = compact(r, key_columns=["a", "b"], keep="last")
    assert len(out.diffs) == 2


def test_compact_invalid_keep_raises():
    r = _make_result(_added({"id": 1}))
    with pytest.raises(ValueError, match="keep must be"):
        compact(r, key_columns=["id"], keep="middle")


def test_compact_removed_row_uses_before():
    r = _make_result(_removed({"id": 99, "v": "gone"}))
    out = compact(r, key_columns=["id"])
    assert len(out.diffs) == 1
    assert out.diffs[0].kind == "removed"


# ---------------------------------------------------------------------------
# merge_results()
# ---------------------------------------------------------------------------

def test_merge_results_combines_distinct_keys():
    r1 = _make_result(_added({"id": 1, "v": "a"}))
    r2 = _make_result(_added({"id": 2, "v": "b"}))
    out = merge_results([r1, r2], key_columns=["id"])
    assert len(out.diffs) == 2


def test_merge_results_deduplicates_across_results():
    r1 = _make_result(_added({"id": 1, "v": "old"}))
    r2 = _make_result(_modified({"id": 1, "v": "old"}, {"id": 1, "v": "new"}))
    out = merge_results([r1, r2], key_columns=["id"], keep="last")
    assert len(out.diffs) == 1
    assert out.diffs[0].kind == "modified"


def test_merge_results_empty_iterable():
    out = merge_results([], key_columns=["id"])
    assert out.diffs == []
