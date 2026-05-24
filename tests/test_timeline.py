"""Tests for sqlsift.timeline."""

from datetime import datetime, timezone, timedelta

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.timeline import Timeline, Snapshot


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _added(key, row):
    return RowDiff(kind="added", key=key, left=None, right=row, delta={})


def _modified(key, left, right, delta):
    return RowDiff(kind="modified", key=key, left=left, right=right, delta=delta)


def _make_result(diffs):
    return DiffResult(diffs=diffs, key_columns=["id"])


def _ts(offset_days=0):
    return datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(days=offset_days)


# ---------------------------------------------------------------------------
# Snapshot
# ---------------------------------------------------------------------------

def test_snapshot_as_dict_keys():
    result = _make_result([])
    snap = Snapshot(result=result, label="v1", recorded_at=_ts())
    d = snap.as_dict()
    assert set(d.keys()) == {"label", "recorded_at", "added", "removed", "modified", "identical"}


def test_snapshot_as_dict_counts():
    diffs = [_added((1,), {"id": 1, "v": "a"})]
    snap = Snapshot(result=_make_result(diffs), label="v1", recorded_at=_ts())
    d = snap.as_dict()
    assert d["added"] == 1
    assert d["removed"] == 0


# ---------------------------------------------------------------------------
# Timeline.add / latest
# ---------------------------------------------------------------------------

def test_add_returns_snapshot():
    tl = Timeline()
    snap = tl.add(_make_result([]), "snap1", recorded_at=_ts())
    assert isinstance(snap, Snapshot)
    assert snap.label == "snap1"


def test_latest_none_when_empty():
    assert Timeline().latest() is None


def test_latest_returns_last():
    tl = Timeline()
    tl.add(_make_result([]), "a", recorded_at=_ts(0))
    tl.add(_make_result([]), "b", recorded_at=_ts(1))
    assert tl.latest().label == "b"


# ---------------------------------------------------------------------------
# Timeline.as_dict_list
# ---------------------------------------------------------------------------

def test_as_dict_list_length():
    tl = Timeline()
    tl.add(_make_result([]), "x", recorded_at=_ts(0))
    tl.add(_make_result([]), "y", recorded_at=_ts(1))
    assert len(tl.as_dict_list()) == 2


def test_as_dict_list_order():
    tl = Timeline()
    tl.add(_make_result([]), "first", recorded_at=_ts(0))
    tl.add(_make_result([]), "second", recorded_at=_ts(1))
    labels = [d["label"] for d in tl.as_dict_list()]
    assert labels == ["first", "second"]


# ---------------------------------------------------------------------------
# Timeline.trend
# ---------------------------------------------------------------------------

def test_trend_modified():
    tl = Timeline()
    tl.add(_make_result([]), "a", recorded_at=_ts(0))
    tl.add(
        _make_result([_modified((1,), {"id": 1}, {"id": 1, "v": 2}, {"v": (1, 2)})]),
        "b",
        recorded_at=_ts(1),
    )
    assert tl.trend("modified") == [0, 1]


def test_trend_invalid_metric_raises():
    tl = Timeline()
    with pytest.raises(ValueError, match="metric must be one of"):
        tl.trend("unknown")


# ---------------------------------------------------------------------------
# Timeline.between
# ---------------------------------------------------------------------------

def test_between_filters_snapshots():
    tl = Timeline()
    tl.add(_make_result([]), "day0", recorded_at=_ts(0))
    tl.add(_make_result([]), "day1", recorded_at=_ts(1))
    tl.add(_make_result([]), "day2", recorded_at=_ts(2))
    sub = tl.between(_ts(1), _ts(2))
    assert len(sub.snapshots) == 2
    assert sub.snapshots[0].label == "day1"


def test_between_empty_range():
    tl = Timeline()
    tl.add(_make_result([]), "day0", recorded_at=_ts(0))
    sub = tl.between(_ts(5), _ts(10))
    assert sub.snapshots == []
