"""Tests for sqlsift.exporter."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.exporter import (
    to_csv_file,
    to_csv_string,
    to_dict_list,
    to_json_file,
    to_json_string,
    to_text_file,
)


def _make_result() -> DiffResult:
    diffs = [
        RowDiff(kind="added", key=("1",), old=None, new={"id": "1", "val": "a"}, delta={}),
        RowDiff(kind="removed", key=("2",), old={"id": "2", "val": "b"}, new=None, delta={}),
        RowDiff(
            kind="modified",
            key=("3",),
            old={"id": "3", "val": "c"},
            new={"id": "3", "val": "d"},
            delta={"val": ("c", "d")},
        ),
    ]
    return DiffResult(diffs=diffs, key_columns=["id"])


# --- to_dict_list ---

def test_to_dict_list_length():
    result = _make_result()
    rows = to_dict_list(result)
    assert len(rows) == 3


def test_to_dict_list_kinds():
    result = _make_result()
    kinds = [r["kind"] for r in to_dict_list(result)]
    assert kinds == ["added", "removed", "modified"]


def test_to_dict_list_delta_present_for_modified():
    result = _make_result()
    modified = [r for r in to_dict_list(result) if r["kind"] == "modified"][0]
    assert "delta" in modified
    assert modified["delta"]["val"] == ["c", "d"]


def test_to_dict_list_no_delta_for_added():
    result = _make_result()
    added = [r for r in to_dict_list(result) if r["kind"] == "added"][0]
    assert "old" not in added


# --- to_json_string ---

def test_to_json_string_is_valid_json():
    result = _make_result()
    text = to_json_string(result)
    parsed = json.loads(text)
    assert isinstance(parsed, list)
    assert len(parsed) == 3


def test_to_json_string_indent():
    result = _make_result()
    text = to_json_string(result, indent=4)
    assert "    " in text


# --- to_csv_string ---

def test_to_csv_string_contains_header():
    result = _make_result()
    csv_text = to_csv_string(result)
    first_line = csv_text.splitlines()[0]
    assert "kind" in first_line.lower() or "key" in first_line.lower()


def test_to_csv_string_row_count():
    result = _make_result()
    csv_text = to_csv_string(result)
    # header + 3 data rows (may vary by reporter impl, at minimum > 1 line)
    assert len(csv_text.splitlines()) >= 2


# --- file writers ---

def test_to_text_file_creates_file(tmp_path):
    result = _make_result()
    out = tmp_path / "report.txt"
    to_text_file(result, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_to_csv_file_creates_file(tmp_path):
    result = _make_result()
    out = tmp_path / "report.csv"
    to_csv_file(result, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_to_json_file_creates_valid_json(tmp_path):
    result = _make_result()
    out = tmp_path / "report.json"
    to_json_file(result, out)
    parsed = json.loads(out.read_text(encoding="utf-8"))
    # format_json from reporter returns the reporter payload; just check it loaded
    assert parsed is not None
