"""Core diffing logic for comparing two query result sets."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple


@dataclass
class RowDiff:
    """Represents a discrepancy between a row in two result sets."""

    key: Tuple[Any, ...]
    status: str  # 'added', 'removed', or 'modified'
    left: Optional[Dict[str, Any]] = None
    right: Optional[Dict[str, Any]] = None
    changed_columns: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"RowDiff(key={self.key!r}, status={self.status!r}, "
            f"changed_columns={self.changed_columns!r})"
        )


@dataclass
class DiffResult:
    """Aggregated result of diffing two result sets."""

    diffs: List[RowDiff] = field(default_factory=list)

    @property
    def added(self) -> List[RowDiff]:
        return [d for d in self.diffs if d.status == "added"]

    @property
    def removed(self) -> List[RowDiff]:
        return [d for d in self.diffs if d.status == "removed"]

    @property
    def modified(self) -> List[RowDiff]:
        return [d for d in self.diffs if d.status == "modified"]

    @property
    def is_equal(self) -> bool:
        return len(self.diffs) == 0

    def summary(self) -> str:
        return (
            f"DiffResult: {len(self.added)} added, "
            f"{len(self.removed)} removed, "
            f"{len(self.modified)} modified"
        )


def diff_results(
    left: Sequence[Dict[str, Any]],
    right: Sequence[Dict[str, Any]],
    key_columns: List[str],
) -> DiffResult:
    """Diff two sequences of row dicts keyed by *key_columns*.

    Args:
        left: The baseline result set (e.g. pre-migration).
        right: The comparison result set (e.g. post-migration).
        key_columns: Column names that uniquely identify a row.

    Returns:
        A :class:`DiffResult` containing all detected discrepancies.
    """
    if not key_columns:
        raise ValueError("At least one key column must be specified.")

    def make_key(row: Dict[str, Any]) -> Tuple[Any, ...]:
        return tuple(row[col] for col in key_columns)

    left_index: Dict[Tuple[Any, ...], Dict[str, Any]] = {make_key(r): r for r in left}
    right_index: Dict[Tuple[Any, ...], Dict[str, Any]] = {make_key(r): r for r in right}

    diffs: List[RowDiff] = []

    for key, left_row in left_index.items():
        if key not in right_index:
            diffs.append(RowDiff(key=key, status="removed", left=left_row))
        else:
            right_row = right_index[key]
            changed = [
                col
                for col in set(left_row) | set(right_row)
                if left_row.get(col) != right_row.get(col)
            ]
            if changed:
                diffs.append(
                    RowDiff(
                        key=key,
                        status="modified",
                        left=left_row,
                        right=right_row,
                        changed_columns=sorted(changed),
                    )
                )

    for key, right_row in right_index.items():
        if key not in left_index:
            diffs.append(RowDiff(key=key, status="added", right=right_row))

    return DiffResult(diffs=diffs)
