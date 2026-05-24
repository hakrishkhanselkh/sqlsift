"""Tests for sqlsift.filter module."""

import pytest
from sqlsift.diff import DiffResult, RowDiff
from sqlsift.filter import by_kind, by_columns, by_predicate


def _make_result() -> DiffResult:
    """Build a DiffResult with one diff of each kind for testing."""
    added = RowDiff(kind="added", key=("id", 3), left=None, right={"id": 3, "v": "c"}, delta=None)
    removed = RowDiff(kind="removed", key=("id", 1), left={"id": 1, "v": "a"}, right=None, delta=None)
    modified = RowDiff(
        kind="modified",
        key=("id", 2),
        left={"id": 2, "v": "b", "score": 10},
        right={"id": 2, "v": "B", "score": 20},
        delta={"v": ("b", "B"), "score": (10, 20)},
    )
    return DiffResult(
        diffs=[added, removed, modified],
        left_only=[{"id": 1, "v": "a"}],
        right_only=[{"id": 3, "v": "c"}],
    )


# --- by_kind ---

def test_by_kind_added():
    result = by_kind(_make_result(), "added")
    assert all(d.kind == "added" for d in result.diffs)
    assert len(result.diffs) == 1


def test_by_kind_removed():
    result = by_kind(_make_result(), "removed")
    assert all(d.kind == "removed" for d in result.diffs)
    assert len(result.diffs) == 1


def test_by_kind_modified():
    result = by_kind(_make_result(), "modified")
    assert all(d.kind == "modified" for d in result.diffs)
    assert len(result.diffs) == 1


def test_by_kind_invalid_raises():
    with pytest.raises(ValueError, match="kind must be one of"):
        by_kind(_make_result(), "unknown")


def test_by_kind_preserves_left_only_for_removed():
    result = by_kind(_make_result(), "removed")
    assert result.left_only == [{"id": 1, "v": "a"}]
    assert result.right_only == []


def test_by_kind_preserves_right_only_for_added():
    result = by_kind(_make_result(), "added")
    assert result.right_only == [{"id": 3, "v": "c"}]
    assert result.left_only == []


# --- by_columns ---

def test_by_columns_keeps_relevant_modified():
    result = by_columns(_make_result(), ["v"])
    modified = [d for d in result.diffs if d.kind == "modified"]
    assert len(modified) == 1
    assert "v" in modified[0].delta
    assert "score" not in modified[0].delta


def test_by_columns_drops_modified_with_no_matching_column():
    result = by_columns(_make_result(), ["nonexistent"])
    modified = [d for d in result.diffs if d.kind == "modified"]
    assert len(modified) == 0


def test_by_columns_passes_through_added_and_removed():
    result = by_columns(_make_result(), ["nonexistent"])
    assert any(d.kind == "added" for d in result.diffs)
    assert any(d.kind == "removed" for d in result.diffs)


# --- by_predicate ---

def test_by_predicate_filters_correctly():
    result = by_predicate(_make_result(), lambda d: d.kind == "modified")
    assert len(result.diffs) == 1
    assert result.diffs[0].kind == "modified"


def test_by_predicate_empty_when_none_match():
    result = by_predicate(_make_result(), lambda d: False)
    assert result.diffs == []


def test_by_predicate_all_when_all_match():
    original = _make_result()
    result = by_predicate(original, lambda d: True)
    assert len(result.diffs) == len(original.diffs)
