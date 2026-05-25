"""Tests for sqlsift.auditor."""
from datetime import datetime, timezone

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.auditor import AuditEntry, build_audit_log, audit_summary


def _added(key, row):
    return RowDiff(kind="added", key=key, row=row, delta=None)


def _removed(key, row):
    return RowDiff(kind="removed", key=key, row=row, delta=None)


def _modified(key, row, delta):
    return RowDiff(kind="modified", key=key, row=row, delta=delta)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


_TS = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# AuditEntry.as_dict
# ---------------------------------------------------------------------------

def test_audit_entry_as_dict_keys():
    entry = AuditEntry(kind="added", key=(1,), columns_affected=["a"], timestamp=_TS)
    d = entry.as_dict()
    assert set(d.keys()) == {"kind", "key", "columns_affected", "timestamp", "metadata"}


def test_audit_entry_timestamp_iso():
    entry = AuditEntry(kind="removed", key=(2,), columns_affected=[], timestamp=_TS)
    assert entry.as_dict()["timestamp"] == "2024-01-01T12:00:00+00:00"


# ---------------------------------------------------------------------------
# build_audit_log
# ---------------------------------------------------------------------------

def test_build_audit_log_empty_result():
    result = _make_result()
    entries = build_audit_log(result, timestamp=_TS)
    assert entries == []


def test_build_audit_log_counts():
    result = _make_result(
        _added((1,), {"id": 1, "v": "x"}),
        _removed((2,), {"id": 2, "v": "y"}),
        _modified((3,), {"id": 3, "v": "a"}, {"v": {"old": "a", "new": "b"}}),
    )
    entries = build_audit_log(result, timestamp=_TS)
    assert len(entries) == 3


def test_build_audit_log_kinds():
    result = _make_result(
        _added((1,), {"id": 1}),
        _removed((2,), {"id": 2}),
    )
    entries = build_audit_log(result, timestamp=_TS)
    kinds = [e.kind for e in entries]
    assert kinds == ["added", "removed"]


def test_build_audit_log_columns_affected_modified():
    result = _make_result(
        _modified((1,), {"id": 1, "a": 1, "b": 2}, {"a": {"old": 1, "new": 9}, "b": {"old": 2, "new": 8}}),
    )
    entries = build_audit_log(result, timestamp=_TS)
    assert entries[0].columns_affected == ["a", "b"]


def test_build_audit_log_columns_affected_added():
    result = _make_result(_added((1,), {"id": 1, "name": "alice"}))
    entries = build_audit_log(result, timestamp=_TS)
    assert set(entries[0].columns_affected) == {"id", "name"}


def test_build_audit_log_fixed_timestamp():
    result = _make_result(_added((1,), {"id": 1}))
    entries = build_audit_log(result, timestamp=_TS)
    assert entries[0].timestamp == _TS


def test_build_audit_log_metadata_propagated():
    result = _make_result(_added((1,), {"id": 1}))
    entries = build_audit_log(result, timestamp=_TS, metadata={"source": "migration_v2"})
    assert entries[0].metadata == {"source": "migration_v2"}


def test_build_audit_log_metadata_independent_copies():
    result = _make_result(_added((1,), {"id": 1}), _added((2,), {"id": 2}))
    entries = build_audit_log(result, timestamp=_TS, metadata={"run": 1})
    entries[0].metadata["extra"] = True
    assert "extra" not in entries[1].metadata


# ---------------------------------------------------------------------------
# audit_summary
# ---------------------------------------------------------------------------

def test_audit_summary_empty():
    summary = audit_summary([])
    assert summary["total"] == 0
    assert summary["by_kind"] == {}
    assert summary["column_frequency"] == {}


def test_audit_summary_counts_by_kind():
    result = _make_result(
        _added((1,), {"id": 1}),
        _added((2,), {"id": 2}),
        _removed((3,), {"id": 3}),
    )
    entries = build_audit_log(result, timestamp=_TS)
    summary = audit_summary(entries)
    assert summary["by_kind"]["added"] == 2
    assert summary["by_kind"]["removed"] == 1


def test_audit_summary_column_frequency():
    result = _make_result(
        _modified((1,), {"id": 1, "price": 10}, {"price": {"old": 10, "new": 20}}),
        _modified((2,), {"id": 2, "price": 5}, {"price": {"old": 5, "new": 6}}),
    )
    entries = build_audit_log(result, timestamp=_TS)
    summary = audit_summary(entries)
    assert summary["column_frequency"]["price"] == 2


def test_audit_summary_total():
    result = _make_result(
        _added((1,), {"id": 1}),
        _modified((2,), {"id": 2}, {"v": {"old": 1, "new": 2}}),
    )
    entries = build_audit_log(result, timestamp=_TS)
    assert audit_summary(entries)["total"] == 2
