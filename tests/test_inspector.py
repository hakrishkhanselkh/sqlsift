"""Tests for sqlsift.inspector."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift import inspector


def _added(row: dict) -> RowDiff:
    return RowDiff(kind="added", row=row, delta=None)


def _removed(row: dict) -> RowDiff:
    return RowDiff(kind="removed", row=row, delta=None)


def _modified(row: dict, delta: dict) -> RowDiff:
    return RowDiff(kind="modified", row=row, delta=delta)


def _make_result(*diffs: RowDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


def test_column_names_empty_result():
    result = _make_result()
    assert inspector.column_names(result) == []


def test_column_names_from_added_rows():
    result = _make_result(_added({"id": 1, "name": "alice"}))
    assert inspector.column_names(result) == ["id", "name"]


def test_column_names_includes_delta_keys():
    result = _make_result(_modified({"id": 1}, {"score": (10, 20)}))
    cols = inspector.column_names(result)
    assert "id" in cols
    assert "score" in cols


def test_column_names_sorted():
    result = _make_result(_added({"z": 1, "a": 2, "m": 3}))
    assert inspector.column_names(result) == ["a", "m", "z"]


def test_row_count_all_kinds():
    result = _make_result(
        _added({"id": 1}),
        _removed({"id": 2}),
        _modified({"id": 3}, {"v": (1, 2)}),
    )
    counts = inspector.row_count(result)
    assert counts == {"added": 1, "removed": 1, "modified": 1}


def test_row_count_empty():
    result = _make_result()
    assert inspector.row_count(result) == {"added": 0, "removed": 0, "modified": 0}


def test_has_column_true():
    result = _make_result(_added({"id": 1, "status": "ok"}))
    assert inspector.has_column(result, "status") is True


def test_has_column_false():
    result = _make_result(_added({"id": 1}))
    assert inspector.has_column(result, "missing") is False


def test_sample_values_returns_distinct():
    result = _make_result(
        _added({"id": 1, "region": "us"}),
        _added({"id": 2, "region": "us"}),
        _added({"id": 3, "region": "eu"}),
    )
    vals = inspector.sample_values(result, "region")
    assert vals == ["us", "eu"]


def test_sample_values_respects_limit():
    result = _make_result(*[_added({"id": i, "x": i}) for i in range(20)])
    vals = inspector.sample_values(result, "x", limit=3)
    assert len(vals) == 3


def test_schema_infers_int():
    result = _make_result(_added({"id": 42}))
    s = inspector.schema(result)
    assert s["id"] == "int"


def test_schema_infers_str():
    result = _make_result(_added({"name": "bob"}))
    s = inspector.schema(result)
    assert s["name"] == "str"


def test_schema_unknown_for_none_only():
    result = _make_result(_added({"col": None}))
    s = inspector.schema(result)
    assert s["col"] == "unknown"


def test_inspect_keys():
    result = _make_result(_added({"id": 1}), _removed({"id": 2}))
    info = inspector.inspect(result)
    assert set(info.keys()) == {"row_count", "total", "columns", "key_columns", "schema"}


def test_inspect_total():
    result = _make_result(_added({"id": 1}), _removed({"id": 2}))
    info = inspector.inspect(result)
    assert info["total"] == 2
