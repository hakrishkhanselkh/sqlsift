# sqlsift.deduplicator

The `deduplicator` module provides utilities for detecting and removing duplicate
`RowDiff` entries from a `DiffResult`. Duplicates can arise when merging results
from multiple sources or when the same row appears more than once in a query.

## Functions

### `by_key(result, key_columns) -> DiffResult`

Removes duplicate `RowDiff` entries that share the same `kind` and key-column
values. The **first** occurrence is retained; all subsequent duplicates are
discarded.

```python
from sqlsift.deduplicator import by_key

clean = by_key(result, key_columns=["id"])
```

**Note:** Two rows with the same key but different `kind` values (e.g. `added`
vs `removed`) are treated as distinct and are both kept.

---

### `by_row(result) -> DiffResult`

Removes `RowDiff` entries that are completely identical — same `kind`, same
`row` values, and same `delta`. Useful after merging results where exact
duplicate diff objects may exist.

```python
from sqlsift.deduplicator import by_row

clean = by_row(result)
```

---

### `duplicates(result, key_columns) -> DiffResult`

Returns **only** the duplicate rows (i.e. the second and subsequent occurrences
for each key). The first occurrence is excluded. This is useful for auditing
how many duplicate diffs exist before deciding whether to drop them.

```python
from sqlsift.deduplicator import duplicates

dupes = duplicates(result, key_columns=["id"])
print(f"Found {len(dupes.diffs)} duplicate rows")
```

---

## Typical workflow

```python
from sqlsift import diff
from sqlsift.merger import merge
from sqlsift.deduplicator import by_key, duplicates

combined = merge(result_a, result_b)

# Inspect duplicates first
dupes = duplicates(combined, key_columns=["order_id"])
if dupes.diffs:
    print(f"Warning: {len(dupes.diffs)} duplicate keys detected")

# Then deduplicate
clean = by_key(combined, key_columns=["order_id"])
```
