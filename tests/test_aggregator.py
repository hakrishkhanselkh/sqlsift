"""Tests for sqlsift.aggregator."""

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.aggregator import aggregate, summary_table, ColumnAggregate


def _added(row, key="id"):
    return RowDiff(kind="added", key={key: row[key]}, row=row, delta=None)


def _removed(row, key="id"):
    return RowDiff(kind="removed", key={key: row[key]}, row=row, delta=None)


def _modified(row, delta, key="id"):
    return RowDiff(kind="modified", key={key: row[key]}, row=row, delta=delta)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# ColumnAggregate helpers
# ---------------------------------------------------------------------------

def test_column_aggregate_mean_zero_count():
    agg = ColumnAggregate(column="price")
    assert agg.mean is None


def test_column_aggregate_as_dict_keys():
    agg = ColumnAggregate(column="price", count=2, total=10.0, minimum=3.0, maximum=7.0)
    d = agg.as_dict()
    assert set(d.keys()) == {"column", "count", "sum", "mean", "min", "max"}
    assert d["mean"] == 5.0


# ---------------------------------------------------------------------------
# aggregate()
# ---------------------------------------------------------------------------

def test_aggregate_empty_result():
    result = _make_result()
    stats = aggregate(result, ["price"])
    assert stats["price"].count == 0
    assert stats["price"].mean is None


def test_aggregate_added_rows():
    result = _make_result(
        _added({"id": 1, "price": 10}),
        _added({"id": 2, "price": 20}),
    )
    stats = aggregate(result, ["price"])
    assert stats["price"].count == 2
    assert stats["price"].total == 30.0
    assert stats["price"].minimum == 10.0
    assert stats["price"].maximum == 20.0
    assert stats["price"].mean == 15.0


def test_aggregate_removed_rows():
    result = _make_result(
        _removed({"id": 1, "qty": 5}),
        _removed({"id": 2, "qty": 15}),
    )
    stats = aggregate(result, ["qty"])
    assert stats["qty"].count == 2
    assert stats["qty"].mean == 10.0


def test_aggregate_modified_uses_new_value():
    result = _make_result(
        _modified({"id": 1, "price": 10}, delta={"price": (10, 50)}),
    )
    stats = aggregate(result, ["price"])
    assert stats["price"].total == 50.0


def test_aggregate_modified_fallback_to_row_when_column_not_in_delta():
    result = _make_result(
        _modified({"id": 1, "price": 99}, delta={"name": ("a", "b")}),
    )
    stats = aggregate(result, ["price"])
    assert stats["price"].total == 99.0


def test_aggregate_skips_non_numeric():
    result = _make_result(
        _added({"id": 1, "label": "foo"}),
    )
    stats = aggregate(result, ["label"])
    assert stats["label"].count == 0


def test_aggregate_kinds_filter():
    result = _make_result(
        _added({"id": 1, "price": 100}),
        _removed({"id": 2, "price": 200}),
    )
    stats = aggregate(result, ["price"], kinds=("added",))
    assert stats["price"].count == 1
    assert stats["price"].total == 100.0


def test_aggregate_multiple_columns():
    result = _make_result(
        _added({"id": 1, "price": 10, "qty": 3}),
        _added({"id": 2, "price": 20, "qty": 7}),
    )
    stats = aggregate(result, ["price", "qty"])
    assert stats["price"].total == 30.0
    assert stats["qty"].total == 10.0


# ---------------------------------------------------------------------------
# summary_table()
# ---------------------------------------------------------------------------

def test_summary_table_returns_list_of_dicts():
    result = _make_result(_added({"id": 1, "price": 5}))
    table = summary_table(result, ["price"])
    assert isinstance(table, list)
    assert len(table) == 1
    assert table[0]["column"] == "price"
