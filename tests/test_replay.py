"""Tests for sqlsift.replay."""
from datetime import datetime, timezone

import pytest

from sqlsift.auditor import AuditEntry
from sqlsift.replay import replay, replay_stats

_TS = datetime(2024, 6, 1, tzinfo=timezone.utc)


def _entry(kind, key, cols=None):
    return AuditEntry(kind=kind, key=key, columns_affected=cols or [], timestamp=_TS)


_BASE_STORE = [
    {"id": 1, "name": "alice", "score": 10},
    {"id": 2, "name": "bob", "score": 20},
    {"id": 3, "name": "carol", "score": 30},
]


# ---------------------------------------------------------------------------
# replay_stats
# ---------------------------------------------------------------------------

def test_replay_stats_empty():
    assert replay_stats([]) == {"added": 0, "removed": 0, "modified": 0}


def test_replay_stats_counts():
    entries = [
        _entry("added", (4,)),
        _entry("removed", (1,)),
        _entry("modified", (2,)),
        _entry("modified", (3,)),
    ]
    stats = replay_stats(entries)
    assert stats == {"added": 1, "removed": 1, "modified": 2}


# ---------------------------------------------------------------------------
# replay – removed
# ---------------------------------------------------------------------------

def test_replay_remove_row():
    entries = [_entry("removed", (2,))]
    result = replay(entries, _BASE_STORE, key_func=lambda r: (r["id"],))
    ids = [r["id"] for r in result]
    assert 2 not in ids
    assert len(result) == 2


def test_replay_remove_nonexistent_row_is_noop():
    entries = [_entry("removed", (99,))]
    result = replay(entries, _BASE_STORE, key_func=lambda r: (r["id"],))
    assert len(result) == len(_BASE_STORE)


# ---------------------------------------------------------------------------
# replay – added
# ---------------------------------------------------------------------------

def test_replay_add_row():
    new_row = {"id": 4, "name": "dave", "score": 40}
    entries = [_entry("added", (4,))]
    result = replay(
        entries,
        _BASE_STORE,
        key_func=lambda r: (r["id"],),
        row_source={(4,): new_row},
    )
    assert len(result) == 4
    assert any(r["id"] == 4 for r in result)


def test_replay_add_row_without_source_is_noop():
    entries = [_entry("added", (4,))]
    result = replay(entries, _BASE_STORE, key_func=lambda r: (r["id"],))
    assert len(result) == len(_BASE_STORE)


# ---------------------------------------------------------------------------
# replay – modified
# ---------------------------------------------------------------------------

def test_replay_modify_row():
    updated = {"id": 1, "name": "alice", "score": 99}
    entries = [_entry("modified", (1,), ["score"])]
    result = replay(
        entries,
        _BASE_STORE,
        key_func=lambda r: (r["id"],),
        row_source={(1,): updated},
    )
    row = next(r for r in result if r["id"] == 1)
    assert row["score"] == 99


def test_replay_modify_nonexistent_is_noop():
    entries = [_entry("modified", (99,), ["score"])]
    result = replay(
        entries,
        _BASE_STORE,
        key_func=lambda r: (r["id"],),
        row_source={(99,): {"id": 99, "score": 0}},
    )
    assert len(result) == len(_BASE_STORE)


# ---------------------------------------------------------------------------
# replay – does not mutate original store
# ---------------------------------------------------------------------------

def test_replay_does_not_mutate_original():
    original = [{"id": 1, "v": 1}]
    entries = [_entry("removed", (1,))]
    replay(entries, original, key_func=lambda r: (r["id"],))
    assert len(original) == 1
