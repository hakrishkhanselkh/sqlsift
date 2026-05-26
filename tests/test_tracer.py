"""Tests for sqlsift.tracer."""

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.tracer import (
    TraceEntry,
    kind_changed,
    persistent_keys,
    trace,
    transient_keys,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _added(row):
    return RowDiff(kind="added", row=row, delta={})


def _removed(row):
    return RowDiff(kind="removed", row=row, delta={})


def _modified(row, delta=None):
    return RowDiff(kind="modified", row=row, delta=delta or {})


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# trace()
# ---------------------------------------------------------------------------

def test_trace_empty_snapshots_returns_empty():
    assert trace([]) == []


def test_trace_single_snapshot_single_row():
    r = _make_result(_added({"id": 1, "val": "a"}))
    entries = trace([("v1", r)], key_columns=["id"])
    assert len(entries) == 1
    assert entries[0].key == (1,)
    assert entries[0].appearances == {"v1": "added"}


def test_trace_two_snapshots_same_key():
    r1 = _make_result(_added({"id": 1}))
    r2 = _make_result(_modified({"id": 1}, {"val": ("a", "b")}))
    entries = trace([("v1", r1), ("v2", r2)], key_columns=["id"])
    assert len(entries) == 1
    assert entries[0].appearances == {"v1": "added", "v2": "modified"}


def test_trace_two_snapshots_different_keys():
    r1 = _make_result(_added({"id": 1}))
    r2 = _make_result(_added({"id": 2}))
    entries = trace([("v1", r1), ("v2", r2)], key_columns=["id"])
    assert len(entries) == 2


def test_trace_no_key_columns_uses_full_row():
    r = _make_result(_added({"id": 1, "name": "alice"}))
    entries = trace([("snap", r)])
    assert len(entries) == 1
    assert entries[0].appearances == {"snap": "added"}


def test_trace_entry_as_dict():
    e = TraceEntry(key=(42,), appearances={"a": "added", "b": "modified"})
    d = e.as_dict()
    assert d["key"] == (42,)
    assert d["appearances"]["a"] == "added"


# ---------------------------------------------------------------------------
# persistent_keys()
# ---------------------------------------------------------------------------

def test_persistent_keys_all_present():
    r1 = _make_result(_added({"id": 1}), _added({"id": 2}))
    r2 = _make_result(_modified({"id": 1}), _removed({"id": 3}))
    entries = trace([("v1", r1), ("v2", r2)], key_columns=["id"])
    persistent = persistent_keys(entries, ["v1", "v2"])
    keys = [e.key for e in persistent]
    assert (1,) in keys
    assert (2,) not in keys
    assert (3,) not in keys


def test_persistent_keys_empty_entries():
    assert persistent_keys([], ["v1", "v2"]) == []


# ---------------------------------------------------------------------------
# transient_keys()
# ---------------------------------------------------------------------------

def test_transient_keys_partial_presence():
    r1 = _make_result(_added({"id": 1}), _added({"id": 2}))
    r2 = _make_result(_modified({"id": 1}))
    entries = trace([("v1", r1), ("v2", r2)], key_columns=["id"])
    transient = transient_keys(entries, ["v1", "v2"])
    keys = [e.key for e in transient]
    assert (2,) in keys
    assert (1,) not in keys


# ---------------------------------------------------------------------------
# kind_changed()
# ---------------------------------------------------------------------------

def test_kind_changed_detects_change():
    r1 = _make_result(_added({"id": 1}), _added({"id": 2}))
    r2 = _make_result(_modified({"id": 1}), _added({"id": 2}))
    entries = trace([("v1", r1), ("v2", r2)], key_columns=["id"])
    changed = kind_changed(entries, "v1", "v2")
    assert len(changed) == 1
    assert changed[0].key == (1,)


def test_kind_changed_no_change_returns_empty():
    r1 = _make_result(_added({"id": 5}))
    r2 = _make_result(_added({"id": 5}))
    entries = trace([("v1", r1), ("v2", r2)], key_columns=["id"])
    assert kind_changed(entries, "v1", "v2") == []


def test_kind_changed_missing_label_skipped():
    r1 = _make_result(_added({"id": 7}))
    entries = trace([("v1", r1)], key_columns=["id"])
    assert kind_changed(entries, "v1", "v2") == []
