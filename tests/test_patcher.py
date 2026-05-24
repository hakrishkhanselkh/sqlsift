"""Tests for sqlsift.patcher."""

import pytest
from sqlsift.diff import DiffResult, RowDiff
from sqlsift.patcher import generate_patch, _quote_value


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_result(diffs, key_columns=("id",)):
    return DiffResult(diffs=diffs, key_columns=tuple(key_columns))


def _added(row):
    return RowDiff(kind="added", key={"id": row["id"]}, left=None, right=row)


def _removed(row):
    return RowDiff(kind="removed", key={"id": row["id"]}, left=row, right=None)


def _modified(left, right):
    return RowDiff(kind="modified", key={"id": left["id"]}, left=left, right=right)


# ---------------------------------------------------------------------------
# _quote_value
# ---------------------------------------------------------------------------

def test_quote_value_none():
    assert _quote_value(None) == "NULL"


def test_quote_value_int():
    assert _quote_value(42) == "42"


def test_quote_value_float():
    assert _quote_value(3.14) == "3.14"


def test_quote_value_bool():
    assert _quote_value(True) == "TRUE"
    assert _quote_value(False) == "FALSE"


def test_quote_value_string_escapes_single_quotes():
    assert _quote_value("O'Brien") == "'O''Brien'"


def test_quote_value_plain_string():
    assert _quote_value("hello") == "'hello'"


# ---------------------------------------------------------------------------
# generate_patch — added rows
# ---------------------------------------------------------------------------

def test_added_row_generates_insert():
    result = _make_result([_added({"id": 1, "name": "Alice"})])
    stmts = generate_patch(result, "users")
    assert len(stmts) == 1
    assert stmts[0].startswith("INSERT INTO users")
    assert "'Alice'" in stmts[0]


# ---------------------------------------------------------------------------
# generate_patch — removed rows
# ---------------------------------------------------------------------------

def test_removed_row_generates_delete():
    result = _make_result([_removed({"id": 7, "name": "Bob"})])
    stmts = generate_patch(result, "users")
    assert len(stmts) == 1
    assert stmts[0] == "DELETE FROM users WHERE id = 7;"


# ---------------------------------------------------------------------------
# generate_patch — modified rows
# ---------------------------------------------------------------------------

def test_modified_row_generates_update():
    left = {"id": 3, "name": "Carol", "age": 30}
    right = {"id": 3, "name": "Carol", "age": 31}
    result = _make_result([_modified(left, right)])
    stmts = generate_patch(result, "users")
    assert len(stmts) == 1
    assert "UPDATE users" in stmts[0]
    assert "age = 31" in stmts[0]
    assert "WHERE id = 3" in stmts[0]


def test_modified_row_with_no_actual_change_skipped():
    row = {"id": 5, "name": "Dave"}
    result = _make_result([_modified(row, dict(row))])
    stmts = generate_patch(result, "users")
    assert stmts == []


# ---------------------------------------------------------------------------
# generate_patch — composite key
# ---------------------------------------------------------------------------

def test_composite_key_delete():
    row = {"tenant_id": 1, "user_id": 9, "role": "admin"}
    diff = RowDiff(
        kind="removed",
        key={"tenant_id": 1, "user_id": 9},
        left=row,
        right=None,
    )
    result = _make_result([diff], key_columns=("tenant_id", "user_id"))
    stmts = generate_patch(result, "memberships")
    assert "tenant_id = 1" in stmts[0]
    assert "user_id = 9" in stmts[0]


# ---------------------------------------------------------------------------
# generate_patch — empty result
# ---------------------------------------------------------------------------

def test_empty_result_returns_empty_list():
    result = _make_result([])
    assert generate_patch(result, "users") == []
