"""Tests for sqlsift.normalizer."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.normalizer import (
    chain,
    normalize_result,
    normalize_row,
    strip_whitespace,
    to_lowercase,
    to_numeric,
)


def _added(key, right):
    return RowDiff(key=key, kind="added", left=None, right=right, delta=None)


def _removed(key, left):
    return RowDiff(key=key, kind="removed", left=left, right=None, delta=None)


def _modified(key, left, right, delta=None):
    return RowDiff(key=key, kind="modified", left=left, right=right, delta=delta or {})


def _make_result(rows):
    return DiffResult(rows=rows, key_columns=["id"])


# --- strip_whitespace ---

def test_strip_whitespace_trims_spaces():
    coercers = strip_whitespace(["name"])
    row = _modified((1,), {"id": 1, "name": "  alice  "}, {"id": 1, "name": "  alice  "})
    result = normalize_row(row, coercers)
    assert result.left["name"] == "alice"
    assert result.right["name"] == "alice"


def test_strip_whitespace_ignores_non_targeted_columns():
    coercers = strip_whitespace(["name"])
    row = _modified((1,), {"id": 1, "city": "  NYC  "}, {"id": 1, "city": "  NYC  "})
    result = normalize_row(row, coercers)
    assert result.left["city"] == "  NYC  "


# --- to_lowercase ---

def test_to_lowercase_converts_strings():
    coercers = to_lowercase(["status"])
    row = _modified((1,), {"id": 1, "status": "ACTIVE"}, {"id": 1, "status": "Inactive"})
    result = normalize_row(row, coercers)
    assert result.left["status"] == "active"
    assert result.right["status"] == "inactive"


# --- to_numeric ---

def test_to_numeric_casts_float():
    coercers = to_numeric(["price"])
    row = _modified((1,), {"id": 1, "price": "9.99"}, {"id": 1, "price": "12.50"})
    result = normalize_row(row, coercers)
    assert result.left["price"] == pytest.approx(9.99)
    assert result.right["price"] == pytest.approx(12.50)


def test_to_numeric_casts_int():
    coercers = to_numeric(["qty"], cast=int)
    row = _modified((1,), {"id": 1, "qty": "3"}, {"id": 1, "qty": "7"})
    result = normalize_row(row, coercers)
    assert result.left["qty"] == 3
    assert isinstance(result.left["qty"], int)


def test_to_numeric_leaves_invalid_values_unchanged():
    coercers = to_numeric(["price"])
    row = _modified((1,), {"id": 1, "price": "n/a"}, {"id": 1, "price": "n/a"})
    result = normalize_row(row, coercers)
    assert result.left["price"] == "n/a"


# --- normalize_row with None sides ---

def test_normalize_row_added_left_is_none():
    coercers = strip_whitespace(["name"])
    row = _added((2,), {"id": 2, "name": "  bob  "})
    result = normalize_row(row, coercers)
    assert result.left is None
    assert result.right["name"] == "bob"


def test_normalize_row_removed_right_is_none():
    coercers = strip_whitespace(["name"])
    row = _removed((3,), {"id": 3, "name": "  carol  "})
    result = normalize_row(row, coercers)
    assert result.right is None
    assert result.left["name"] == "carol"


# --- normalize_result ---

def test_normalize_result_applies_to_all_rows():
    rows = [
        _modified((1,), {"id": 1, "name": "  alice  "}, {"id": 1, "name": "  ALICE  "}),
        _added((2,), {"id": 2, "name": "  bob  "}),
    ]
    result = _make_result(rows)
    coercers = chain(strip_whitespace(["name"]), to_lowercase(["name"]))
    normalized = normalize_result(result, coercers)
    assert normalized.rows[0].left["name"] == "alice"
    assert normalized.rows[0].right["name"] == "alice"
    assert normalized.rows[1].right["name"] == "bob"


def test_normalize_result_preserves_key_columns():
    result = _make_result([])
    normalized = normalize_result(result, {})
    assert normalized.key_columns == ["id"]


# --- chain ---

def test_chain_later_dict_overrides_earlier():
    d1 = {"col": str.strip}
    d2 = {"col": str.upper}
    merged = chain(d1, d2)
    assert merged["col"]("+hello+") == "+HELLO+"


def test_chain_merges_distinct_columns():
    d1 = {"a": str.strip}
    d2 = {"b": str.upper}
    merged = chain(d1, d2)
    assert set(merged.keys()) == {"a", "b"}
