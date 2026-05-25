"""Tests for sqlsift.matcher."""

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.matcher import exact_match, find_by_key, fuzzy_match


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _added(row):
    return RowDiff(kind="added", before=None, after=row, delta={})


def _removed(row):
    return RowDiff(kind="removed", before=row, after=None, delta={})


def _modified(before, after):
    delta = {k: (before[k], after[k]) for k in before if before[k] != after.get(k)}
    return RowDiff(kind="modified", before=before, after=after, delta=delta)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# exact_match
# ---------------------------------------------------------------------------

def test_exact_match_finds_added_row():
    r = _make_result(_added({"id": 1, "name": "Alice"}))
    found = exact_match(r, ["id"], {"id": 1})
    assert len(found) == 1
    assert found[0].after["name"] == "Alice"


def test_exact_match_finds_removed_row():
    r = _make_result(_removed({"id": 2, "name": "Bob"}))
    found = exact_match(r, ["id"], {"id": 2})
    assert len(found) == 1


def test_exact_match_uses_before_for_modified():
    r = _make_result(_modified({"id": 3, "val": "old"}, {"id": 3, "val": "new"}))
    found = exact_match(r, ["id"], {"id": 3})
    assert len(found) == 1


def test_exact_match_no_results_when_no_match():
    r = _make_result(_added({"id": 1, "name": "Alice"}))
    found = exact_match(r, ["id"], {"id": 99})
    assert found == []


def test_exact_match_empty_columns_raises():
    r = _make_result()
    with pytest.raises(ValueError, match="columns must not be empty"):
        exact_match(r, [], {})


def test_exact_match_composite_key():
    r = _make_result(
        _added({"org": "A", "dept": "eng", "count": 5}),
        _added({"org": "A", "dept": "hr", "count": 2}),
    )
    found = exact_match(r, ["org", "dept"], {"org": "A", "dept": "eng"})
    assert len(found) == 1
    assert found[0].after["count"] == 5


# ---------------------------------------------------------------------------
# fuzzy_match
# ---------------------------------------------------------------------------

def test_fuzzy_match_finds_similar_string():
    r = _make_result(_added({"id": 1, "name": "Jonathan"}))
    found = fuzzy_match(r, "name", "Jonathon", threshold=0.7)
    assert len(found) == 1


def test_fuzzy_match_excludes_dissimilar():
    r = _make_result(_added({"id": 1, "name": "Zephyr"}))
    found = fuzzy_match(r, "name", "Alice", threshold=0.9)
    assert found == []


def test_fuzzy_match_invalid_threshold_raises():
    r = _make_result()
    with pytest.raises(ValueError, match="threshold"):
        fuzzy_match(r, "name", "x", threshold=1.5)


def test_fuzzy_match_skips_none_values():
    r = _make_result(_added({"id": 1, "name": None}))
    found = fuzzy_match(r, "name", "Alice")
    assert found == []


# ---------------------------------------------------------------------------
# find_by_key
# ---------------------------------------------------------------------------

def test_find_by_key_returns_correct_row():
    r = _make_result(
        _added({"id": 10, "v": "x"}),
        _added({"id": 20, "v": "y"}),
    )
    diff = find_by_key(r, ["id"], [10])
    assert diff is not None
    assert diff.after["v"] == "x"


def test_find_by_key_returns_none_when_missing():
    r = _make_result(_added({"id": 1}))
    assert find_by_key(r, ["id"], [999]) is None


def test_find_by_key_mismatched_lengths_raises():
    r = _make_result()
    with pytest.raises(ValueError):
        find_by_key(r, ["id", "org"], [1])
