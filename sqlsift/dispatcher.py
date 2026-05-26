"""sqlsift.dispatcher — apply per-bucket callbacks to routed DiffResults."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from sqlsift.diff import DiffResult

Handler = Callable[[str, DiffResult], Any]


class Dispatcher:
    """Register handlers for named buckets and dispatch a routing dict.

    Example::

        d = Dispatcher()
        d.register("new_rows", lambda name, dr: print(f"{name}: {len(dr.diffs)} rows"))
        d.dispatch(routing)
    """

    def __init__(self, default_handler: Optional[Handler] = None) -> None:
        self._handlers: Dict[str, Handler] = {}
        self._default: Optional[Handler] = default_handler

    # ------------------------------------------------------------------
    def register(self, bucket: str, handler: Handler) -> "Dispatcher":
        """Register *handler* for *bucket*. Returns self for chaining."""
        self._handlers[bucket] = handler
        return self

    def unregister(self, bucket: str) -> None:
        """Remove the handler for *bucket* (no-op if absent)."""
        self._handlers.pop(bucket, None)

    # ------------------------------------------------------------------
    def dispatch(
        self,
        routing: Dict[str, DiffResult],
        *,
        raise_on_missing: bool = False,
    ) -> Dict[str, Any]:
        """Call the registered handler for each bucket.

        Returns a dict mapping bucket name → handler return value.
        Buckets with no registered handler use the default handler if set;
        otherwise they are skipped (or raise if *raise_on_missing* is True).
        """
        results: Dict[str, Any] = {}
        for name, dr in routing.items():
            handler = self._handlers.get(name, self._default)
            if handler is None:
                if raise_on_missing:
                    raise KeyError(f"No handler registered for bucket {name!r}")
                continue
            results[name] = handler(name, dr)
        return results

    # ------------------------------------------------------------------
    def registered_buckets(self) -> List[str]:
        """Return sorted list of explicitly registered bucket names."""
        return sorted(self._handlers.keys())

    def __len__(self) -> int:
        return len(self._handlers)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Dispatcher(buckets={self.registered_buckets()})"
