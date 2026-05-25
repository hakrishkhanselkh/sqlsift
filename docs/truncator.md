# sqlsift.truncator

The `truncator` module provides helpers for **capping the size** of a `DiffResult`.
This is useful when you want to preview a large diff, limit output for display
purposes, or feed a manageable slice into downstream steps.

---

## Functions

### `by_count(result, n, *, kind=None) -> DiffResult`

Return a new `DiffResult` containing **at most `n` rows**.

| Parameter | Type | Description |
|-----------|------|-------------|
| `result` | `DiffResult` | Source result to truncate. |
| `n` | `int` | Maximum number of rows to keep. Must be ≥ 0. |
| `kind` | `str \| None` | If given, the limit applies only to rows of this kind (`'added'`, `'removed'`, `'modified'`). Other kinds are kept in full. |

```python
from sqlsift.truncator import by_count

preview = by_count(result, 10)
first_10_added = by_count(result, 10, kind="added")
```

---

### `by_fraction(result, fraction, *, kind=None) -> DiffResult`

Return a new `DiffResult` keeping **`fraction`** of the rows (a float in `[0.0, 1.0]`).

The actual count is computed as `int(total * fraction)`, then delegated to
`by_count`.

```python
from sqlsift.truncator import by_fraction

half = by_fraction(result, 0.5)
half_modified = by_fraction(result, 0.5, kind="modified")
```

---

### `drop_beyond(result, limit) -> DiffResult`

Hard-cap the result to `limit` rows total, regardless of kind.  
Equivalent to `by_count(result, limit)`.

```python
from sqlsift.truncator import drop_beyond

small = drop_beyond(result, 100)
```

---

## Notes

- All functions return a **new** `DiffResult`; the original is never mutated.
- `key_columns` is preserved on the returned result.
- Row order from the source result is maintained; truncation always removes
  rows from the **end** of the sequence.
