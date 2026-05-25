"""auditor.py – track which rows changed between two DiffResults.

Provides utilities for producing an audit trail that records what changed,
when it was recorded, and which keys were affected.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlsift.diff import DiffResult, RowDiff


@dataclass
class AuditEntry:
    """A single entry in an audit log."""

    kind: str
    key: tuple
    columns_affected: List[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "key": list(self.key),
            "columns_affected": self.columns_affected,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


def _columns_affected(row_diff: RowDiff) -> List[str]:
    """Return the list of columns that differ for a RowDiff."""
    if row_diff.delta:
        return sorted(row_diff.delta.keys())
    if row_diff.row:
        return sorted(row_diff.row.keys())
    return []


def build_audit_log(
    result: DiffResult,
    *,
    timestamp: Optional[datetime] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> List[AuditEntry]:
    """Convert a DiffResult into a list of AuditEntry objects.

    Parameters
    ----------
    result:
        The diff result to audit.
    timestamp:
        Optional fixed timestamp to stamp every entry with.
    metadata:
        Optional dict merged into every entry's metadata field.
    """
    ts = timestamp or datetime.now(timezone.utc)
    meta = metadata or {}
    entries: List[AuditEntry] = []
    for row_diff in result.diffs:
        entries.append(
            AuditEntry(
                kind=row_diff.kind,
                key=row_diff.key,
                columns_affected=_columns_affected(row_diff),
                timestamp=ts,
                metadata=dict(meta),
            )
        )
    return entries


def audit_summary(entries: List[AuditEntry]) -> Dict[str, Any]:
    """Return a high-level summary dict for a list of AuditEntry objects."""
    counts: Dict[str, int] = {}
    all_columns: Dict[str, int] = {}
    for entry in entries:
        counts[entry.kind] = counts.get(entry.kind, 0) + 1
        for col in entry.columns_affected:
            all_columns[col] = all_columns.get(col, 0) + 1
    return {
        "total": len(entries),
        "by_kind": counts,
        "column_frequency": all_columns,
    }
