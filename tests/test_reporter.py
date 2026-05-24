"""Tests for sqlsift.reporter formatting utilities."""

import json
import io

import pytest

from sqlsift.diff import DiffResult, RowDiff
from sqlsift.reporter import format_text, format_csv, format_json, print_report


def _make_result(*diffs: RowDiff) -> DiffResult:
    return DiffResult(list(diffs))


@pytest.fixture()
def sample_result() -> DiffResult:
    return _make_result(
        RowDiff(key=1, status="added", old_row={}, new_row={"id": 1, "name": "Alice"}),
        RowDiff(key=2, status="removed", old_row={"id": 2, "name": "Bob"}, new_row={}),
        RowDiff(
            key=3,
            status="modified",
            old_row={"id": 3, "name": "Carol", "age": 30},
            new_row={"id": 3, "name": "Carol", "age": 31},
        ),
    )


def test_format_text_summary(sample_result):
    output = format_text(sample_result)
    assert "1 added" in output
    assert "1 removed" in output
    assert "1 modified" in output


def test_format_text_added_label(sample_result):
    output = format_text(sample_result)
    assert "[ADDED]" in output


def test_format_text_removed_label(sample_result):
    output = format_text(sample_result)
    assert "[REMOVED]" in output


def test_format_text_modified_shows_delta(sample_result):
    output = format_text(sample_result)
    assert "[MODIFIED]" in output
    assert "age" in output
    assert "30" in output
    assert "31" in output


def test_format_csv_has_header(sample_result):
    output = format_csv(sample_result)
    assert output.startswith("status,key,column,old_value,new_value")


def test_format_csv_modified_row_per_column(sample_result):
    output = format_csv(sample_result)
    lines = [l for l in output.splitlines() if "modified" in l]
    assert len(lines) == 1  # only 'age' changed
    assert "age" in lines[0]


def test_format_json_valid(sample_result):
    output = format_json(sample_result)
    data = json.loads(output)
    assert data["summary"]["added"] == 1
    assert data["summary"]["removed"] == 1
    assert data["summary"]["modified"] == 1
    assert len(data["diffs"]) == 3


def test_format_json_diff_keys(sample_result):
    data = json.loads(format_json(sample_result))
    for diff in data["diffs"]:
        assert {"status", "key", "old_row", "new_row"} <= diff.keys()


def test_print_report_writes_to_file(sample_result):
    buf = io.StringIO()
    print_report(sample_result, fmt="text", file=buf)
    assert len(buf.getvalue()) > 0


def test_print_report_unknown_format_raises(sample_result):
    with pytest.raises(ValueError, match="Unknown format"):
        print_report(sample_result, fmt="xml")  # type: ignore[arg-type]


def test_empty_result_text():
    result = _make_result()
    output = format_text(result)
    assert "0 added" in output
    assert "0 removed" in output
    assert "0 modified" in output
