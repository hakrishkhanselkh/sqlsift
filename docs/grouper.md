# sqlsift.grouper

The `grouper` module lets you **partition a `DiffResult` into labelled sub-results** based on the values of one or more columns. This is useful when you want to analyse discrepancies per region, environment, tenant, or any other categorical dimension.

## Functions

### `by_column(result, column) → Dict[str, DiffResult]`

Split *result* into a dictionary of `DiffResult` objects, one per distinct value of *column*.

```python
from sqlsift.grouper import by_column

groups = by_column(diff_result, "region")
for region, sub in groups.items():
    print(f"{region}: {len(sub.diffs)} diffs")
```

Rows that do not contain the specified column are placed under the key `"<missing>"`.

---

### `by_columns(result, columns) → Dict[Tuple[str, ...], DiffResult]`

Like `by_column`, but groups by a **composite key** formed from multiple columns.

```python
from sqlsift.grouper import by_columns

groups = by_columns(diff_result, ["region", "env"])
for (region, env), sub in groups.items():
    print(f"{region}/{env}: {len(sub.diffs)} diffs")
```

---

### `counts_by_column(result, column) → Dict[str, int]`

Convenience wrapper that returns a plain `{value: count}` dict instead of full `DiffResult` objects.

```python
from sqlsift.grouper import counts_by_column

print(counts_by_column(diff_result, "status"))
# {'active': 12, 'inactive': 3}
```

---

## Integration with other modules

The sub-results returned by the grouper are ordinary `DiffResult` instances, so you can pass them directly to any other sqlsift module:

```python
from sqlsift.grouper import by_column
from sqlsift.reporter import format_text
from sqlsift.summarizer import summarize

for region, sub in by_column(diff_result, "region").items():
    print(f"=== {region} ===")
    print(format_text(sub))
    s = summarize(sub)
    print(s.as_dict())
```
