"""Tests for sqlsift.streaker."""

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.streaker import Streak, find_streaks, longest_streak, streak_summary


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _added(row: dict) -> RowDiff:
    return RowDiff(kind="added", row=row, delta={})


def _removed(row: dict) -> RowDiff:
    return RowDiff(kind="removed", row=row, delta={})


def _modified(row: dict, delta: dict) -> RowDiff:
    return RowDiff(kind="modified", row=row, delta=delta)


def _make_result(*diffs: RowDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# Streak dataclass
# ---------------------------------------------------------------------------

def test_streak_length():
    d = _added({"id": 1})
    s = Streak(key=(1,), kind="added", rows=[d, d])
    assert s.length == 2


def test_streak_as_dict_keys():
    d = _added({"id": 1})
    s = Streak(key=(1,), kind="added", rows=[d])
    result = s.as_dict()
    assert set(result.keys()) == {"key", "kind", "length", "rows"}


# ---------------------------------------------------------------------------
# find_streaks
# ---------------------------------------------------------------------------

def test_find_streaks_empty_result():
    result = _make_result()
    assert find_streaks(result, ["id"]) == []


def test_find_streaks_no_run_long_enough():
    # Only single-item groups — default min_length=2 should return nothing
    result = _make_result(
        _added({"id": 1, "v": "a"}),
        _removed({"id": 2, "v": "b"}),
    )
    assert find_streaks(result, ["id"]) == []


def test_find_streaks_detects_run_of_added():
    # Same key appearing twice with same kind
    d1 = _added({"id": 1, "v": "a"})
    d2 = _added({"id": 1, "v": "b"})
    result = _make_result(d1, d2)
    streaks = find_streaks(result, ["id"])
    assert len(streaks) == 1
    assert streaks[0].kind == "added"
    assert streaks[0].length == 2


def test_find_streaks_run_broken_by_different_kind():
    d1 = _added({"id": 1, "v": "a"})
    d2 = _removed({"id": 1, "v": "b"})
    d3 = _removed({"id": 1, "v": "c"})
    result = _make_result(d1, d2, d3)
    # Only the two "removed" form a streak of length 2
    streaks = find_streaks(result, ["id"])
    assert len(streaks) == 1
    assert streaks[0].kind == "removed"


def test_find_streaks_multiple_keys_independent():
    d1 = _added({"id": 1, "v": "x"})
    d2 = _added({"id": 1, "v": "y"})
    d3 = _removed({"id": 2, "v": "a"})
    d4 = _removed({"id": 2, "v": "b"})
    result = _make_result(d1, d2, d3, d4)
    streaks = find_streaks(result, ["id"])
    assert len(streaks) == 2
    kinds = {s.kind for s in streaks}
    assert kinds == {"added", "removed"}


def test_find_streaks_min_length_respected():
    d1 = _added({"id": 1, "v": "a"})
    d2 = _added({"id": 1, "v": "b"})
    d3 = _added({"id": 1, "v": "c"})
    result = _make_result(d1, d2, d3)
    assert len(find_streaks(result, ["id"], min_length=3)) == 1
    assert len(find_streaks(result, ["id"], min_length=4)) == 0


# ---------------------------------------------------------------------------
# longest_streak
# ---------------------------------------------------------------------------

def test_longest_streak_empty_returns_none():
    assert longest_streak(_make_result(), ["id"]) is None


def test_longest_streak_picks_max():
    d = _added({"id": 1, "v": "x"})
    e = _removed({"id": 2, "v": "y"})
    result = _make_result(d, d, d, e, e)
    s = longest_streak(result, ["id"])
    assert s is not None
    assert s.length == 3
    assert s.kind == "added"


# ---------------------------------------------------------------------------
# streak_summary
# ---------------------------------------------------------------------------

def test_streak_summary_empty():
    summary = streak_summary(_make_result(), ["id"])
    assert summary["total_streaks"] == 0
    assert summary["max_length"] == 0
    assert summary["by_kind"] == {}


def test_streak_summary_counts():
    d = _added({"id": 1, "v": "a"})
    e = _removed({"id": 2, "v": "b"})
    result = _make_result(d, d, e, e)
    summary = streak_summary(result, ["id"])
    assert summary["total_streaks"] == 2
    assert summary["max_length"] == 2
    assert summary["by_kind"]["added"] == 1
    assert summary["by_kind"]["removed"] == 1
