"""pipeline.py – lightweight functional pipeline for chaining DiffResult operations."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional

from sqlsift.diff import DiffResult

_Step = Callable[[DiffResult], DiffResult]


class Pipeline:
    """Chain multiple :class:`~sqlsift.diff.DiffResult` transformations.

    Each *step* is a callable that accepts and returns a ``DiffResult``.

    Example
    -------
    >>> from sqlsift.pipeline import Pipeline
    >>> from sqlsift.transformer import drop_columns
    >>> from sqlsift.filter import by_kind
    >>>
    >>> result = (
    ...     Pipeline(diff_result)
    ...     .pipe(drop_columns, columns=["_ts"])
    ...     .pipe(by_kind, kind="modified")
    ...     .run()
    ... )
    """

    def __init__(self, source: DiffResult) -> None:
        self._source = source
        self._steps: List[_Step] = []

    # ------------------------------------------------------------------
    # Builder API
    # ------------------------------------------------------------------

    def pipe(self, fn: Callable[..., DiffResult], **kwargs: Any) -> "Pipeline":
        """Append a transformation step.

        Parameters
        ----------
        fn:
            A callable with signature ``fn(diff_result, **kwargs) -> DiffResult``.
        **kwargs:
            Extra keyword arguments forwarded to *fn* (the ``DiffResult`` is
            always the first positional argument).
        """
        self._steps.append(lambda r, _fn=fn, _kw=kwargs: _fn(r, **_kw))
        return self

    def run(self) -> DiffResult:
        """Execute all steps in order and return the final :class:`~sqlsift.diff.DiffResult`."""
        result = self._source
        for step in self._steps:
            result = step(result)
        return result

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of registered steps."""
        return len(self._steps)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Pipeline(steps={len(self._steps)}, rows={len(self._source.diffs)})"


def build(
    source: DiffResult,
    steps: Iterable[_Step],
) -> DiffResult:
    """Apply an iterable of pre-bound step callables to *source* in order.

    Each callable must accept a single ``DiffResult`` and return a new one.

    Parameters
    ----------
    source:
        Starting ``DiffResult``.
    steps:
        Iterable of ``Callable[[DiffResult], DiffResult]``.

    Returns
    -------
    DiffResult
        Result after all steps have been applied.
    """
    result = source
    for step in steps:
        result = step(result)
    return result
