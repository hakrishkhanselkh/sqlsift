"""Summarizer module: compute aggregate statistics from a DiffResult."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from sqlsift.diff import DiffResult, RowDiff


@dataclass
class ColumnStats:
    """Statistics about how often a specific column differed."""

    column: str
    change_count: int = 0

    @property
    def as_dict(self) -> Dict[str, object]:
        return {"column": self.column, "change_count": self.change_count}


@dataclass
class DiffSummary:
    """High-level summary of a DiffResult."""

    total_rows_compared: int
    added_count: int
    removed_count: int
    modified_count: int
    unchanged_count: int
    column_stats: List[ColumnStats] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return (self.added_count + self.removed_count + self.modified_count) > 0

    def as_dict(self) -> Dict[str, object]:
        return {
            "total_rows_compared": self.total_rows_compared,
            "added": self.added_count,
            "removed": self.removed_count,
            "modified": self.modified_count,
            "unchanged": self.unchanged_count,
            "has_differences": self.has_differences,
            "column_stats": [cs.as_dict for cs in self.column_stats],
        }


def summarize(result: DiffResult, total_rows_compared: int = 0) -> DiffSummary:
    """Compute a DiffSummary from a DiffResult.

    Args:
        result: The DiffResult produced by sqlsift.diff.compare.
        total_rows_compared: Optional hint for the total number of rows
            evaluated (e.g. max of left/right row counts). When omitted or
            zero, it is inferred from the diff counts.

    Returns:
        A DiffSummary instance with per-kind counts and per-column change stats.
    """
    added = len(result.added)
    removed = len(result.removed)
    modified = len(result.modified)

    inferred_total = added + removed + modified
    if total_rows_compared <= 0:
        total_rows_compared = inferred_total

    unchanged = max(0, total_rows_compared - inferred_total)

    # Tally which columns appear most in modified diffs
    col_counts: Dict[str, int] = {}
    diff: RowDiff
    for diff in result.modified:
        for col in (diff.diff or {}):
            col_counts[col] = col_counts.get(col, 0) + 1

    column_stats = [
        ColumnStats(column=col, change_count=count)
        for col, count in sorted(col_counts.items(), key=lambda kv: -kv[1])
    ]

    return DiffSummary(
        total_rows_compared=total_rows_compared,
        added_count=added,
        removed_count=removed,
        modified_count=modified,
        unchanged_count=unchanged,
        column_stats=column_stats,
    )
