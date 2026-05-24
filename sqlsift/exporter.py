"""Export DiffResult data to various file formats."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Union

from sqlsift.diff import DiffResult
from sqlsift.reporter import format_csv, format_json, format_text


def to_text_file(result: DiffResult, path: Union[str, Path]) -> None:
    """Write a human-readable diff report to *path*."""
    content = format_text(result)
    Path(path).write_text(content, encoding="utf-8")


def to_csv_file(result: DiffResult, path: Union[str, Path]) -> None:
    """Write diff rows as CSV to *path*."""
    content = format_csv(result)
    Path(path).write_text(content, encoding="utf-8")


def to_json_file(result: DiffResult, path: Union[str, Path]) -> None:
    """Write diff rows as JSON to *path*."""
    content = format_json(result)
    Path(path).write_text(content, encoding="utf-8")


def to_dict_list(result: DiffResult) -> list[dict]:
    """Return diff rows as a plain list of dicts, suitable for further processing."""
    rows = []
    for diff in result.diffs:
        entry: dict = {"kind": diff.kind, "key": diff.key}
        if diff.old is not None:
            entry["old"] = dict(diff.old)
        if diff.new is not None:
            entry["new"] = dict(diff.new)
        if diff.delta:
            entry["delta"] = {col: list(vals) for col, vals in diff.delta.items()}
        rows.append(entry)
    return rows


def to_csv_string(result: DiffResult) -> str:
    """Return diff rows serialised as a CSV string."""
    return format_csv(result)


def to_json_string(result: DiffResult, indent: int = 2) -> str:
    """Return diff rows serialised as a JSON string."""
    payload = to_dict_list(result)
    return json.dumps(payload, indent=indent, default=str)
