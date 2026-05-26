# sqlsift.indexer

The `indexer` module builds fast lookup structures over a `DiffResult`, enabling
key-based access, duplicate grouping, and gap detection.

## Functions

### `build(result, key_columns) -> dict`

Returns a `{key_tuple: RowDiff}` dictionary.  When multiple rows share the same
key the last one wins.

```python
from sqlsift.indexer import build

idx = build(result, key_columns=["id"])
row = idx.get((42,))
```

### `lookup(result, key_columns, key_values) -> RowDiff | None`

Convenience wrapper around `build`.  Pass `key_values` as a plain dict.

```python
from sqlsift.indexer import lookup

row = lookup(result, ["id"], {"id": 42})
if row:
    print(row.kind, row.after)
```

### `group_by_key(result, key_columns) -> dict`

Like `build` but maps each key to a **list** of `RowDiff` objects.  Useful
after a `merger.merge` call where duplicate keys may exist.

```python
from sqlsift.indexer import group_by_key

groups = group_by_key(merged, ["id"])
for key, rows in groups.items():
    print(key, len(rows))
```

### `key_set(result, key_columns) -> set`

Returns the set of all key tuples present in the result.

```python
from sqlsift.indexer import key_set

keys = key_set(result, ["org", "dept"])
```

### `missing_keys(result, key_columns, expected_keys) -> list`

Given a list of expected key dicts, returns those that are absent from
`result`.

```python
from sqlsift.indexer import missing_keys

gaps = missing_keys(result, ["id"], [{"id": 1}, {"id": 2}, {"id": 3}])
for g in gaps:
    print("missing:", g)
```

## Notes

- For removed rows the key is derived from `row.before`; for all others from
  `row.after`.
- All functions are pure — they do not mutate the source `DiffResult`.
