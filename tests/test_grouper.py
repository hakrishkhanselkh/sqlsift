"""Tests for sqlsift.grouper."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.grouper import by_column, by_columns, counts_by_column


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _added(row: dict, key=("id",)) -> RowDiff:
    return RowDiff(kind="added", key={k: row[k] for k in key}, left=None, right=row)


def _removed(row: dict, key=("id",)) -> RowDiff:
    return RowDiff(kind="removed", key={k: row[k] for k in key}, left=row, right=None)


def _modified(left: dict, right: dict, key=("id",)) -> RowDiff:
    delta = {k: (left[k], right[k]) for k in right if left.get(k) != right.get(k)}
    return RowDiff(kind="modified", key={k: left[k] for k in key}, left=left, right=right, delta=delta)


def _make_result(*diffs: RowDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# by_column
# ---------------------------------------------------------------------------

def test_by_column_empty_result():
    result = _make_result()
    groups = by_column(result, "region")
    assert groups == {}


def test_by_column_single_group():
    r1 = _added({"id": 1, "region": "EU"})
    r2 = _added({"id": 2, "region": "EU"})
    groups = by_column(_make_result(r1, r2), "region")
    assert set(groups.keys()) == {"EU"}
    assert len(groups["EU"].diffs) == 2


def test_by_column_multiple_groups():
    r1 = _added({"id": 1, "region": "EU"})
    r2 = _added({"id": 2, "region": "US"})
    r3 = _removed({"id": 3, "region": "EU"})
    groups = by_column(_make_result(r1, r2, r3), "region")
    assert set(groups.keys()) == {"EU", "US"}
    assert len(groups["EU"].diffs) == 2
    assert len(groups["US"].diffs) == 1


def test_by_column_missing_column_key():
    r1 = _added({"id": 1})
    groups = by_column(_make_result(r1), "region")
    assert "<missing>" in groups


def test_by_column_returns_diff_result_instances():
    r1 = _added({"id": 1, "region": "EU"})
    groups = by_column(_make_result(r1), "region")
    assert isinstance(groups["EU"], DiffResult)


# ---------------------------------------------------------------------------
# by_columns
# ---------------------------------------------------------------------------

def test_by_columns_composite_key():
    r1 = _added({"id": 1, "region": "EU", "env": "prod"})
    r2 = _added({"id": 2, "region": "EU", "env": "staging"})
    r3 = _added({"id": 3, "region": "US", "env": "prod"})
    groups = by_columns(_make_result(r1, r2, r3), ["region", "env"])
    assert ("EU", "prod") in groups
    assert ("EU", "staging") in groups
    assert ("US", "prod") in groups


def test_by_columns_single_column_matches_by_column():
    r1 = _added({"id": 1, "region": "EU"})
    r2 = _added({"id": 2, "region": "US"})
    result = _make_result(r1, r2)
    single = by_columns(result, ["region"])
    assert set(k[0] for k in single.keys()) == {"EU", "US"}


# ---------------------------------------------------------------------------
# counts_by_column
# ---------------------------------------------------------------------------

def test_counts_by_column_values():
    r1 = _added({"id": 1, "region": "EU"})
    r2 = _added({"id": 2, "region": "EU"})
    r3 = _added({"id": 3, "region": "US"})
    counts = counts_by_column(_make_result(r1, r2, r3), "region")
    assert counts == {"EU": 2, "US": 1}


def test_counts_by_column_empty():
    counts = counts_by_column(_make_result(), "region")
    assert counts == {}
