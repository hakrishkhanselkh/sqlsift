"""Tests for sqlsift.pipeline."""

from __future__ import annotations

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.pipeline import Pipeline, build
from sqlsift.transformer import drop_columns, rename_columns, transform_rows


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _added(key, row):
    return RowDiff(kind="added", key=key, row=row, delta=None)


def _modified(key, row, delta):
    return RowDiff(kind="modified", key=key, row=row, delta=delta)


def _make_result(*diffs):
    return DiffResult(diffs=list(diffs))


# ---------------------------------------------------------------------------
# Pipeline class
# ---------------------------------------------------------------------------

def test_pipeline_run_no_steps_returns_source():
    source = _make_result(_added((1,), {"id": 1}))
    result = Pipeline(source).run()
    assert len(result.diffs) == 1


def test_pipeline_len_reflects_steps():
    source = _make_result()
    p = Pipeline(source)
    assert len(p) == 0
    p.pipe(drop_columns, columns=["x"])
    assert len(p) == 1


def test_pipeline_pipe_returns_self_for_chaining():
    source = _make_result()
    p = Pipeline(source)
    returned = p.pipe(drop_columns, columns=[])
    assert returned is p


def test_pipeline_applies_steps_in_order():
    rd = _added((1,), {"id": 1, "name": "  alice  ", "secret": "x"})
    source = _make_result(rd)
    result = (
        Pipeline(source)
        .pipe(transform_rows, transforms={"name": str.strip})
        .pipe(drop_columns, columns=["secret"])
        .run()
    )
    row = result.diffs[0].row
    assert row["name"] == "alice"
    assert "secret" not in row


def test_pipeline_rename_then_transform():
    rd = _added((1,), {"id": 1, "usr": "  bob  "})
    source = _make_result(rd)
    result = (
        Pipeline(source)
        .pipe(rename_columns, rename_map={"usr": "name"})
        .pipe(transform_rows, transforms={"name": str.strip})
        .run()
    )
    assert result.diffs[0].row["name"] == "bob"
    assert "usr" not in result.diffs[0].row


def test_pipeline_does_not_mutate_source():
    rd = _added((1,), {"id": 1, "val": "x"})
    source = _make_result(rd)
    Pipeline(source).pipe(transform_rows, transforms={"val": str.upper}).run()
    assert source.diffs[0].row["val"] == "x"


# ---------------------------------------------------------------------------
# build() helper
# ---------------------------------------------------------------------------

def test_build_empty_steps_returns_source():
    source = _make_result(_added((1,), {"id": 1}))
    result = build(source, [])
    assert len(result.diffs) == 1


def test_build_applies_pre_bound_steps():
    rd = _added((1,), {"id": 1, "tag": "  py  ", "tmp": 0})
    source = _make_result(rd)
    steps = [
        lambda r: transform_rows(r, {"tag": str.strip}),
        lambda r: drop_columns(r, ["tmp"]),
    ]
    result = build(source, steps)
    row = result.diffs[0].row
    assert row["tag"] == "py"
    assert "tmp" not in row


def test_build_with_multiple_rows():
    rows = [_added((i,), {"id": i, "v": " x "}) for i in range(5)]
    source = _make_result(*rows)
    result = build(source, [lambda r: transform_rows(r, {"v": str.strip})])
    assert all(d.row["v"] == "x" for d in result.diffs)
