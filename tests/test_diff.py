"""Tests for sqlsift.diff — row-level result set diffing."""

import pytest

from sqlsift.diff import DiffResult, RowDiff, diff_results


BASE_ROWS = [
    {"id": 1, "name": "Alice", "score": 10},
    {"id": 2, "name": "Bob", "score": 20},
    {"id": 3, "name": "Carol", "score": 30},
]


def test_identical_sets_produce_no_diffs():
    result = diff_results(BASE_ROWS, BASE_ROWS, key_columns=["id"])
    assert result.is_equal
    assert result.summary() == "DiffResult: 0 added, 0 removed, 0 modified"


def test_added_row_detected():
    right = BASE_ROWS + [{"id": 4, "name": "Dave", "score": 40}]
    result = diff_results(BASE_ROWS, right, key_columns=["id"])
    assert len(result.added) == 1
    assert result.added[0].key == (4,)
    assert result.added[0].right["name"] == "Dave"
    assert result.removed == []
    assert result.modified == []


def test_removed_row_detected():
    right = [r for r in BASE_ROWS if r["id"] != 2]
    result = diff_results(BASE_ROWS, right, key_columns=["id"])
    assert len(result.removed) == 1
    assert result.removed[0].key == (2,)
    assert result.removed[0].left["name"] == "Bob"


def test_modified_row_detected():
    right = [
        {"id": 1, "name": "Alice", "score": 99},  # score changed
        {"id": 2, "name": "Bob", "score": 20},
        {"id": 3, "name": "Carol", "score": 30},
    ]
    result = diff_results(BASE_ROWS, right, key_columns=["id"])
    assert len(result.modified) == 1
    diff = result.modified[0]
    assert diff.key == (1,)
    assert "score" in diff.changed_columns
    assert diff.left["score"] == 10
    assert diff.right["score"] == 99


def test_composite_key():
    left = [{"tenant": "A", "id": 1, "val": "x"}]
    right = [{"tenant": "A", "id": 1, "val": "y"}]
    result = diff_results(left, right, key_columns=["tenant", "id"])
    assert len(result.modified) == 1
    assert result.modified[0].key == ("A", 1)
    assert "val" in result.modified[0].changed_columns


def test_empty_key_columns_raises():
    with pytest.raises(ValueError, match="At least one key column"):
        diff_results(BASE_ROWS, BASE_ROWS, key_columns=[])


def test_empty_result_sets():
    result = diff_results([], [], key_columns=["id"])
    assert result.is_equal


def test_row_diff_repr():
    rd = RowDiff(key=(1,), status="modified", changed_columns=["score"])
    assert "modified" in repr(rd)
    assert "score" in repr(rd)


def test_diff_result_summary_counts():
    right = [
        {"id": 1, "name": "Alice", "score": 99},  # modified
        # id=2 removed
        {"id": 3, "name": "Carol", "score": 30},
        {"id": 4, "name": "Dave", "score": 40},   # added
    ]
    result = diff_results(BASE_ROWS, right, key_columns=["id"])
    assert len(result.added) == 1
    assert len(result.removed) == 1
    assert len(result.modified) == 1
    assert "1 added" in result.summary()
    assert "1 removed" in result.summary()
    assert "1 modified" in result.summary()
