"""Tests for sqlsift.indexer."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.indexer import build, group_by_key, key_set, lookup, missing_keys


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _added(row: dict) -> RowDiff:
    return RowDiff(kind="added", before=None, after=row, delta={})


def _removed(row: dict) -> RowDiff:
    return RowDiff(kind="removed", before=row, after=None, delta={})


def _modified(before: dict, after: dict, delta: dict | None = None) -> RowDiff:
    return RowDiff(kind="modified", before=before, after=after, delta=delta or {})


def _make_result(*diffs: RowDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def test_build_empty_result_returns_empty_dict():
    assert build(_make_result(), ["id"]) == {}


def test_build_indexes_added_row():
    r = _make_result(_added({"id": 1, "name": "alice"}))
    idx = build(r, ["id"])
    assert (1,) in idx


def test_build_indexes_removed_row_via_before():
    r = _make_result(_removed({"id": 7, "name": "bob"}))
    idx = build(r, ["id"])
    assert (7,) in idx


def test_build_composite_key():
    r = _make_result(_added({"org": "a", "dept": "eng", "val": 10}))
    idx = build(r, ["org", "dept"])
    assert ("a", "eng") in idx


def test_build_last_row_wins_on_duplicate_key():
    r1 = _added({"id": 1, "v": "first"})
    r2 = _added({"id": 1, "v": "second"})
    idx = build(_make_result(r1, r2), ["id"])
    assert idx[(1,)].after["v"] == "second"


# ---------------------------------------------------------------------------
# lookup
# ---------------------------------------------------------------------------

def test_lookup_finds_existing_row():
    r = _make_result(_added({"id": 42, "name": "carol"}))
    found = lookup(r, ["id"], {"id": 42})
    assert found is not None
    assert found.after["name"] == "carol"


def test_lookup_returns_none_for_missing_key():
    r = _make_result(_added({"id": 1, "name": "dave"}))
    assert lookup(r, ["id"], {"id": 999}) is None


# ---------------------------------------------------------------------------
# group_by_key
# ---------------------------------------------------------------------------

def test_group_by_key_collects_duplicates():
    r1 = _added({"id": 5, "v": "x"})
    r2 = _modified({"id": 5, "v": "x"}, {"id": 5, "v": "y"})
    groups = group_by_key(_make_result(r1, r2), ["id"])
    assert len(groups[(5,)]) == 2


def test_group_by_key_empty_result():
    assert group_by_key(_make_result(), ["id"]) == {}


# ---------------------------------------------------------------------------
# key_set
# ---------------------------------------------------------------------------

def test_key_set_returns_all_keys():
    r = _make_result(
        _added({"id": 1}),
        _added({"id": 2}),
        _removed({"id": 3}),
    )
    ks = key_set(r, ["id"])
    assert ks == {(1,), (2,), (3,)}


# ---------------------------------------------------------------------------
# missing_keys
# ---------------------------------------------------------------------------

def test_missing_keys_detects_absent_entries():
    r = _make_result(_added({"id": 1}), _added({"id": 2}))
    expected = [{"id": 1}, {"id": 2}, {"id": 3}]
    missing = missing_keys(r, ["id"], expected)
    assert missing == [{"id": 3}]


def test_missing_keys_empty_when_all_present():
    r = _make_result(_added({"id": 10}), _added({"id": 20}))
    assert missing_keys(r, ["id"], [{"id": 10}, {"id": 20}]) == []


def test_missing_keys_all_missing():
    r = _make_result()
    expected = [{"id": 1}, {"id": 2}]
    assert missing_keys(r, ["id"], expected) == expected
