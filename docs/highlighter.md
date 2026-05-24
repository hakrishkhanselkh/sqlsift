# sqlsift.highlighter

The `highlighter` module surfaces *which* columns changed in each diff row and
produces display-ready representations with changed values visually marked.

## Functions

### `changed_columns(diff: RowDiff) -> set[str]`

Returns the set of column names that differ for a given `RowDiff`.

- **modified** rows: only columns listed in `delta` where old ≠ new.
- **added / removed** rows: every column in `row` (all values are "new" or
  "gone").
- **identical** rows: empty set.

```python
from sqlsift.highlighter import changed_columns

cols = changed_columns(diff)  # e.g. {'price', 'stock'}
```

### `highlight_row(diff: RowDiff, marker: str = "**") -> dict[str, str]`

Returns a `str`-valued copy of `diff.row` where every changed value is
wrapped with `marker` on both sides.

```python
from sqlsift.highlighter import highlight_row

row = highlight_row(diff)          # {'id': '1', 'price': '**9.99**'}
row = highlight_row(diff, marker=">>")  # {'id': '1', 'price': '>>9.99<<'}
```

> **Note:** the same string is used as both prefix and suffix, mirroring
> Markdown bold (`**value**`) by default.

### `highlight_result(result, marker="**", kinds=("added","removed","modified")) -> list[dict]`

Applies `highlight_row` to every diff in a `DiffResult`, filtering by
`kinds`.  Identical rows are excluded unless explicitly requested.

```python
from sqlsift.highlighter import highlight_result

rows = highlight_result(result)
for r in rows:
    print(r)
```

### `columns_changed_in_result(result: DiffResult) -> dict[str, int]`

Returns a frequency map of column name → number of rows in which that
column changed.  Useful for quickly identifying the most volatile columns
across a migration.

```python
from sqlsift.highlighter import columns_changed_in_result

counts = columns_changed_in_result(result)
# {'price': 42, 'status': 7}
```

## Example

```python
import sqlsift

old = [{"id": 1, "price": 5.0}, {"id": 2, "price": 3.0}]
new = [{"id": 1, "price": 6.5}, {"id": 2, "price": 3.0}]

result = sqlsift.diff(old, new, keys=["id"])
for row in sqlsift.highlight_result(result):
    print(row)
# {'id': '1', 'price': '**6.5**'}
```
