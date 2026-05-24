"""annotator.py – attach human-readable labels / notes to RowDiff objects."""

from __future__ import annotations

from typing import Callable, Dict, List, Optional

from sqlsift.diff import DiffResult, RowDiff

# A rule is a callable that receives a RowDiff and returns a note string or None.
AnnotationRule = Callable[[RowDiff], Optional[str]]


def _default_label(diff: RowDiff) -> str:
    """Return a short label based on the diff kind."""
    return diff.kind.upper()


def annotate_row(diff: RowDiff, rules: List[AnnotationRule]) -> Dict:
    """Apply *rules* to *diff* and return an annotation dict.

    The returned dict always contains:
    - ``key``   – the row key tuple
    - ``kind``  – added / removed / modified
    - ``label`` – default kind label
    - ``notes`` – list of non-None strings produced by the rules
    """
    notes = [note for rule in rules for note in (rule(diff),) if note is not None]
    return {
        "key": diff.key,
        "kind": diff.kind,
        "label": _default_label(diff),
        "notes": notes,
    }


def annotate_result(
    result: DiffResult,
    rules: Optional[List[AnnotationRule]] = None,
) -> List[Dict]:
    """Annotate every diff in *result* using the supplied *rules*.

    If *rules* is omitted or empty only the default label is attached.

    Returns a list of annotation dicts ordered the same as
    ``result.diffs``.
    """
    effective_rules: List[AnnotationRule] = rules or []
    return [annotate_row(d, effective_rules) for d in result.diffs]


def rule_column_changed(column: str, message: Optional[str] = None) -> AnnotationRule:
    """Return a rule that fires when *column* appears in a modified diff's delta."""

    def _rule(diff: RowDiff) -> Optional[str]:
        if diff.kind == "modified" and diff.delta and column in diff.delta:
            return message or f"column '{column}' changed"
        return None

    return _rule


def rule_missing_value(column: str, message: Optional[str] = None) -> AnnotationRule:
    """Return a rule that fires when *column* is None/missing in the new row."""

    def _rule(diff: RowDiff) -> Optional[str]:
        row = diff.new_row or {}
        if row.get(column) is None:
            return message or f"column '{column}' is null or missing"
        return None

    return _rule
