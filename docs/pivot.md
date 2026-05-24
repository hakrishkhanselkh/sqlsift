# sqlsift.pivot

The `pivot` module transforms a `DiffResult` into **column-oriented** summaries,
making it easy to understand *which* columns are changing most and *what* values
are involved.

## Functions

### `by_column(result) -> dict`

Returns a nested mapping:

```
{
  "column_name": {
    "old": [...],   # previous values (modified rows)
    "new": [...],   # new values (modified rows)
    "added": [...], # values from added rows
    "removed": [...]
  },
  ...
}
```

```python
from sqlsift.pivot import by_column

pivoted = by_column(diff_result)
print(pivoted["price"]["old"])  # all old prices that changed
print(pivoted["price"]["new"])  # all new prices
```

### `change_frequency(result) -> dict`

Counts how many *modified* diffs touched each column.

```python
from sqlsift.pivot import change_frequency

freq = change_frequency(diff_result)
# {'price': 42, 'status': 17, 'name': 3}
```

### `most_changed_columns(result, top_n=5) -> list`

Returns the column names ranked by modification frequency.

```python
from sqlsift.pivot import most_changed_columns

hot_cols = most_changed_columns(diff_result, top_n=3)
print(hot_cols)  # ['price', 'status', 'name']
```

## Use-case

After a data migration you may have thousands of modified rows spread across
dozens of columns. `pivot` lets you quickly answer:

- "Which columns changed the most?"
- "What were the before/after values for `status`?"
