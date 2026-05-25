# sqlsift.comparator

Column-level value comparison utilities that operate on `DiffResult` objects.

## Overview

While `sqlsift.diff` surfaces *which* rows changed, `sqlsift.comparator` lets
you drill into *how* specific columns changed across the result set.

## API

### `values_equal(a, b, *, coerce=False) -> bool`

Return `True` when `a` and `b` should be considered equal.

When `coerce=True` string representations of numbers are coerced before
comparison, so `values_equal("1", 1, coerce=True)` returns `True`.

### `column_delta(row, column) -> dict | None`

Return `{"before": ..., "after": ...}` for the named column in a *modified*
row, or `None` if the column did not change or the row is not modified.

### `changed_in_column(result, column) -> list[RowDiff]`

Return every modified row in *result* where *column* appears in the delta.

```python
rows = changed_in_column(result, "status")
```

### `compare_column(result, column, predicate=None) -> list[dict]`

For every modified row return a record:

```python
{"key": ..., "column": "price", "before": 9.99, "after": 14.99}
```

Supply an optional `predicate(before, after) -> bool` to filter rows.

```python
big_jumps = compare_column(result, "price", predicate=lambda b, a: a / b > 1.5)
```

### `numeric_drift(result, column, *, coerce=True) -> list[dict]`

Like `compare_column` but also computes `diff = after - before` and skips
non-numeric columns silently.

```python
drift = numeric_drift(result, "revenue")
for d in drift:
    print(d["key"], d["diff"])
```

## Example

```python
from sqlsift import diff
from sqlsift.comparator import numeric_drift

result = diff.compare(old_rows, new_rows, key="id")
for record in numeric_drift(result, "salary"):
    print(f"{record['key']}: {record['before']} -> {record['after']} ({record['diff']:+}")
```
