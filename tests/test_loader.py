"""Tests for sqlsift.loader."""

import io
import json

import pytest

from sqlsift.loader import from_csv, from_dicts, from_json, from_tuples


# ---------------------------------------------------------------------------
# from_dicts
# ---------------------------------------------------------------------------

def test_from_dicts_returns_copies():
    original = [{"id": 1, "name": "alice"}]
    rows = from_dicts(original)
    rows[0]["name"] = "bob"
    assert original[0]["name"] == "alice"


def test_from_dicts_empty():
    assert from_dicts([]) == []


# ---------------------------------------------------------------------------
# from_csv
# ---------------------------------------------------------------------------

CSV_DATA = """id,name,score
1,alice,95
2,bob,87
"""


def test_from_csv_string():
    rows = from_csv(CSV_DATA)
    assert len(rows) == 2
    assert rows[0] == {"id": "1", "name": "alice", "score": "95"}


def test_from_csv_file_like():
    rows = from_csv(io.StringIO(CSV_DATA))
    assert rows[1]["name"] == "bob"


def test_from_csv_custom_delimiter():
    tsv = "id\tname\n1\talice\n"
    rows = from_csv(tsv, delimiter="\t")
    assert rows[0] == {"id": "1", "name": "alice"}


def test_from_csv_empty_body():
    rows = from_csv("id,name\n")
    assert rows == []


# ---------------------------------------------------------------------------
# from_json
# ---------------------------------------------------------------------------

def test_from_json_string():
    data = json.dumps([{"id": 1, "val": "x"}, {"id": 2, "val": "y"}])
    rows = from_json(data)
    assert len(rows) == 2
    assert rows[0]["val"] == "x"


def test_from_json_file_like():
    data = json.dumps([{"id": 3}])
    rows = from_json(io.StringIO(data))
    assert rows[0]["id"] == 3


def test_from_json_raises_on_non_list():
    with pytest.raises(ValueError, match="top-level array"):
        from_json(json.dumps({"key": "value"}))


def test_from_json_empty_array():
    assert from_json("[]") == []


# ---------------------------------------------------------------------------
# from_tuples
# ---------------------------------------------------------------------------

def test_from_tuples_basic():
    rows = from_tuples([(1, "alice"), (2, "bob")], columns=["id", "name"])
    assert rows == [{"id": 1, "name": "alice"}, {"id": 2, "name": "bob"}]


def test_from_tuples_empty():
    assert from_tuples([], columns=["id", "name"]) == []


def test_from_tuples_raises_on_length_mismatch():
    with pytest.raises(ValueError, match="3 values but 2 columns"):
        from_tuples([(1, 2, 3)], columns=["a", "b"])
