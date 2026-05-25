"""Tests for sqlsift.splitter."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.splitter import by_column_value, by_predicate, by_size


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _added(row: dict, key=("id",)) -> RowDiff:
    return RowDiff(kind="added", key={k: row[k] for k in key}, left=None, right=row)


def _removed(row: dict, key=("id",)) -> RowDiff:
    return RowDiff(kind="removed", key={k: row[k] for k in key}, left=row, right=None)


def _modified(left: dict, right: dict, key=("id",)) -> RowDiff:
    delta = {k: (left[k], right[k]) for k in left if left.get(k) != right.get(k)}
    return RowDiff(kind="modified", key={k: left[k] for k in key}, left=left, right=right, delta=delta)


def _make_result(*diffs: RowDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# by_column_value
# ---------------------------------------------------------------------------

def test_by_column_value_empty_result():
    result = _make_result()
    parts = by_column_value(result, "region")
    assert parts == {}


def test_by_column_value_groups_correctly():
    r1 = _added({"id": 1, "region": "eu"})
    r2 = _added({"id": 2, "region": "us"})
    r3 = _modified({"id": 3, "region": "eu", "v": 1}, {"id": 3, "region": "eu", "v": 2})
    result = _make_result(r1, r2, r3)
    parts = by_column_value(result, "region")
    assert set(parts.keys()) == {"eu", "us"}
    assert len(parts["eu"].diffs) == 2
    assert len(parts["us"].diffs) == 1


def test_by_column_value_missing_column_grouped_under_missing_key():
    r1 = _added({"id": 1})
    result = _make_result(r1)
    parts = by_column_value(result, "region")
    assert "__missing__" in parts
    assert len(parts["__missing__"].diffs) == 1


def test_by_column_value_returns_diff_result_instances():
    r1 = _added({"id": 1, "region": "eu"})
    result = _make_result(r1)
    parts = by_column_value(result, "region")
    assert isinstance(parts["eu"], DiffResult)


# ---------------------------------------------------------------------------
# by_size
# ---------------------------------------------------------------------------

def test_by_size_empty_result_returns_single_empty_chunk():
    result = _make_result()
    chunks = by_size(result, 5)
    assert len(chunks) == 1
    assert chunks[0].diffs == []


def test_by_size_exact_multiple():
    diffs = [_added({"id": i}) for i in range(6)]
    result = DiffResult(diffs=diffs)
    chunks = by_size(result, 3)
    assert len(chunks) == 2
    assert all(len(c.diffs) == 3 for c in chunks)


def test_by_size_remainder_chunk():
    diffs = [_added({"id": i}) for i in range(7)]
    result = DiffResult(diffs=diffs)
    chunks = by_size(result, 3)
    assert len(chunks) == 3
    assert len(chunks[-1].diffs) == 1


def test_by_size_invalid_chunk_size_raises():
    result = _make_result()
    with pytest.raises(ValueError):
        by_size(result, 0)


# ---------------------------------------------------------------------------
# by_predicate
# ---------------------------------------------------------------------------

def test_by_predicate_splits_correctly():
    r1 = _added({"id": 1})
    r2 = _removed({"id": 2})
    r3 = _modified({"id": 3, "v": 1}, {"id": 3, "v": 2})
    result = _make_result(r1, r2, r3)
    matched, unmatched = by_predicate(result, lambda d: d.kind == "added")
    assert len(matched.diffs) == 1
    assert matched.diffs[0].kind == "added"
    assert len(unmatched.diffs) == 2


def test_by_predicate_all_match():
    diffs = [_added({"id": i}) for i in range(4)]
    result = DiffResult(diffs=diffs)
    matched, unmatched = by_predicate(result, lambda _: True)
    assert len(matched.diffs) == 4
    assert len(unmatched.diffs) == 0


def test_by_predicate_none_match():
    diffs = [_added({"id": i}) for i in range(3)]
    result = DiffResult(diffs=diffs)
    matched, unmatched = by_predicate(result, lambda _: False)
    assert len(matched.diffs) == 0
    assert len(unmatched.diffs) == 3


def test_by_predicate_returns_diff_result_instances():
    result = _make_result(_added({"id": 1}))
    matched, unmatched = by_predicate(result, lambda d: d.kind == "added")
    assert isinstance(matched, DiffResult)
    assert isinstance(unmatched, DiffResult)
