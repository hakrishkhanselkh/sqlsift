# sqlsift.profiler

The `profiler` module computes **per-column value profiles** from a `DiffResult`,
giving you a quick statistical snapshot of what values appear across added,
removed, and modified rows.

## API

### `ColumnProfile`

A dataclass holding the profile for a single column.

| Attribute | Type | Description |
|---|---|---|
| `column` | `str` | Column name |
| `total` | `int` | Number of rows that contained this column |
| `null_count` | `int` | Rows where the value was `None` |
| `unique_values` | `int` | Count of distinct non-null values |
| `top_values` | `list[tuple]` | Most frequent `(value, count)` pairs |

Call `.as_dict()` to get a serialisable dictionary that also includes
`null_rate` (float, 0–1).

### `profile_column(result, column, top_n=5)`

Build a `ColumnProfile` for a single *column* over every row in *result*.

```python
from sqlsift.profiler import profile_column

p = profile_column(diff_result, "status", top_n=3)
print(p.as_dict())
# {'column': 'status', 'total': 120, 'null_count': 4,
#  'null_rate': 0.0333, 'unique_values': 3,
#  'top_values': [('active', 80), ('inactive', 36), ('pending', 4)]}
```

### `profile_result(result, columns=None, top_n=5)`

Profile **all** columns in *result* (or an explicit subset) and return a
`dict[str, ColumnProfile]`.

```python
from sqlsift.profiler import profile_result

profiles = profile_result(diff_result)
for col, p in profiles.items():
    print(col, p.null_count, p.unique_values)
```

Pass `columns=["id", "amount"]` to restrict profiling to those columns only.

## Use cases

- Quickly spot columns that gained many `NULL` values after a migration.
- Identify columns with unexpectedly high cardinality in changed rows.
- Feed `top_values` into downstream reporting or alerting logic.
