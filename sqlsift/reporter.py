"""Formatting and reporting utilities for DiffResult output."""

from __future__ import annotations

from typing import IO, Literal, Optional
import sys

from sqlsift.diff import DiffResult, RowDiff

OutputFormat = Literal["text", "csv", "json"]


def _row_to_str(row: dict) -> str:
    return ", ".join(f"{k}={v!r}" for k, v in sorted(row.items()))


def format_text(result: DiffResult) -> str:
    """Return a human-readable summary of a DiffResult."""
    lines: list[str] = []
    lines.append(f"Summary: {result.added_count} added, "
                 f"{result.removed_count} removed, "
                 f"{result.modified_count} modified")
    for diff in result.diffs:
        if diff.status == "added":
            lines.append(f"  [ADDED]    {_row_to_str(diff.new_row)}")
        elif diff.status == "removed":
            lines.append(f"  [REMOVED]  {_row_to_str(diff.old_row)}")
        elif diff.status == "modified":
            changed = {
                k: (diff.old_row.get(k), diff.new_row.get(k))
                for k in set(diff.old_row) | set(diff.new_row)
                if diff.old_row.get(k) != diff.new_row.get(k)
            }
            changes = ", ".join(
                f"{k}: {old!r} -> {new!r}" for k, (old, new) in sorted(changed.items())
            )
            lines.append(f"  [MODIFIED] key={diff.key!r} changes=({changes})")
    return "\n".join(lines)


def format_csv(result: DiffResult) -> str:
    """Return a CSV representation of all row-level diffs."""
    import csv
    import io

    buf = io.StringIO()
    fieldnames = ["status", "key", "column", "old_value", "new_value"]
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()

    for diff in result.diffs:
        if diff.status == "added":
            writer.writerow({"status": "added", "key": diff.key,
                             "column": "", "old_value": "", "new_value": ""})
        elif diff.status == "removed":
            writer.writerow({"status": "removed", "key": diff.key,
                             "column": "", "old_value": "", "new_value": ""})
        elif diff.status == "modified":
            for col in sorted(set(diff.old_row) | set(diff.new_row)):
                old_val = diff.old_row.get(col)
                new_val = diff.new_row.get(col)
                if old_val != new_val:
                    writer.writerow({"status": "modified", "key": diff.key,
                                     "column": col, "old_value": old_val,
                                     "new_value": new_val})
    return buf.getvalue()


def format_json(result: DiffResult) -> str:
    """Return a JSON representation of all row-level diffs."""
    import json

    records = []
    for diff in result.diffs:
        records.append({
            "status": diff.status,
            "key": diff.key,
            "old_row": diff.old_row,
            "new_row": diff.new_row,
        })
    return json.dumps({"summary": {
        "added": result.added_count,
        "removed": result.removed_count,
        "modified": result.modified_count,
    }, "diffs": records}, indent=2, default=str)


def print_report(
    result: DiffResult,
    fmt: OutputFormat = "text",
    file: Optional[IO[str]] = None,
) -> None:
    """Print a formatted report to *file* (defaults to stdout)."""
    file = file or sys.stdout
    formatters = {"text": format_text, "csv": format_csv, "json": format_json}
    if fmt not in formatters:
        raise ValueError(f"Unknown format {fmt!r}. Choose from {list(formatters)}.")
    print(formatters[fmt](result), file=file)
