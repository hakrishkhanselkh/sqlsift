"""Tests for sqlsift.windower."""

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.windower import by_index, by_key_range, rolling_counts


def _added(key, **kw):
    row = {"id": key, **kw}
    return RowDiff(kind="added", key=(key,), old_row=None, new_row=row, delta={})


def _removed(key, **kw):
    row = {"id": key, **kw}
    return RowDiff(kind="removed", key=(key,), old_row=row, new_row=None, delta={})


def _modified(key, **kw):
    row = {"id": key, **kw}
    return RowDiff(kind="modified", key=(key,), old_row=row, new_row=row, delta={"val": (0, 1)})


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# by_index
# ---------------------------------------------------------------------------

def test_by_index_empty_result_yields_nothing():
    result = _make_result()
    windows = list(by_index(result, size=3))
    assert windows == []


def test_by_index_single_window():
    result = _make_result(_added(1), _added(2), _added(3))
    windows = list(by_index(result, size=3))
    assert len(windows) == 1
    assert len(windows[0].diffs) == 3


def test_by_index_multiple_windows():
    result = _make_result(_added(1), _added(2), _added(3), _added(4), _added(5))
    windows = list(by_index(result, size=3, step=1))
    assert len(windows) == 5  # windows starting at 0,1,2,3,4


def test_by_index_step_equals_size_non_overlapping():
    result = _make_result(_added(1), _added(2), _added(3), _added(4))
    windows = list(by_index(result, size=2, step=2))
    assert len(windows) == 2
    assert len(windows[0].diffs) == 2
    assert len(windows[1].diffs) == 2


def test_by_index_last_window_may_be_smaller():
    result = _make_result(_added(1), _added(2), _added(3))
    windows = list(by_index(result, size=2, step=2))
    assert len(windows) == 2
    assert len(windows[-1].diffs) == 1


def test_by_index_invalid_size_raises():
    result = _make_result(_added(1))
    with pytest.raises(ValueError, match="size"):
        list(by_index(result, size=0))


def test_by_index_invalid_step_raises():
    result = _make_result(_added(1))
    with pytest.raises(ValueError, match="step"):
        list(by_index(result, size=1, step=0))


# ---------------------------------------------------------------------------
# by_key_range
# ---------------------------------------------------------------------------

def test_by_key_range_empty_result():
    result = _make_result()
    out = by_key_range(result, "id", 1, 5)
    assert out.diffs == []


def test_by_key_range_filters_correctly():
    result = _make_result(_added(1), _added(3), _added(5), _added(7))
    out = by_key_range(result, "id", 3, 5)
    assert len(out.diffs) == 2
    ids = [d.new_row["id"] for d in out.diffs]
    assert sorted(ids) == [3, 5]


def test_by_key_range_inclusive_boundaries():
    result = _make_result(_added(2), _added(4), _added(6))
    out = by_key_range(result, "id", 2, 6)
    assert len(out.diffs) == 3


def test_by_key_range_uses_old_row_for_removed():
    result = _make_result(_removed(10), _removed(20))
    out = by_key_range(result, "id", 10, 10)
    assert len(out.diffs) == 1


# ---------------------------------------------------------------------------
# rolling_counts
# ---------------------------------------------------------------------------

def test_rolling_counts_empty_result():
    result = _make_result()
    counts = list(rolling_counts(result, size=3))
    assert counts == []


def test_rolling_counts_yields_correct_keys():
    result = _make_result(_added(1), _removed(2), _modified(3))
    counts = list(rolling_counts(result, size=3))
    assert len(counts) == 1
    idx, c = counts[0]
    assert idx == 0
    assert set(c.keys()) == {"added", "removed", "modified"}


def test_rolling_counts_values():
    result = _make_result(_added(1), _added(2), _removed(3))
    _, c = list(rolling_counts(result, size=3))[0]
    assert c["added"] == 2
    assert c["removed"] == 1
    assert c["modified"] == 0


def test_rolling_counts_index_increments():
    result = _make_result(_added(1), _added(2), _added(3), _added(4))
    indices = [idx for idx, _ in rolling_counts(result, size=2, step=2)]
    assert indices == [0, 1]
