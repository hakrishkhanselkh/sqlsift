# sqlsift.auditor

The `auditor` module converts a `DiffResult` into a structured **audit log** —
a list of `AuditEntry` objects that record *what* changed, *which columns* were
affected, and *when* the audit was captured.

## Quick start

```python
from sqlsift import diff
from sqlsift.auditor import build_audit_log, audit_summary

old = [{"id": 1, "price": 10}, {"id": 2, "price": 20}]
new = [{"id": 1, "price": 15}, {"id": 3, "price": 5}]

result = diff.compare(old, new, key="id")
entries = build_audit_log(result, metadata={"migration": "v3"})

for entry in entries:
    print(entry.as_dict())

print(audit_summary(entries))
```

## API

### `AuditEntry`

A dataclass with the following fields:

| Field | Type | Description |
|---|---|---|
| `kind` | `str` | `"added"`, `"removed"`, or `"modified"` |
| `key` | `tuple` | The row's primary key tuple |
| `columns_affected` | `list[str]` | Sorted list of changed column names |
| `timestamp` | `datetime` | UTC timestamp of the audit capture |
| `metadata` | `dict` | Arbitrary key/value metadata |

Call `.as_dict()` to serialise an entry to a plain dictionary.

---

### `build_audit_log(result, *, timestamp=None, metadata=None)`

Convert a `DiffResult` into a list of `AuditEntry` objects.

- **`result`** – the `DiffResult` to audit.
- **`timestamp`** – optional fixed `datetime`; defaults to `datetime.now(UTC)`.
- **`metadata`** – optional dict merged (by copy) into every entry.

Returns `list[AuditEntry]`.

---

### `audit_summary(entries)`

Produce a high-level summary from a list of `AuditEntry` objects.

Returns a dict with:

```python
{
    "total": int,
    "by_kind": {"added": int, "removed": int, "modified": int},
    "column_frequency": {"col_name": int, ...},
}
```

## Notes

- For `modified` rows, `columns_affected` is derived from the `delta` keys.
- For `added` / `removed` rows, `columns_affected` lists all columns in the row.
- Each `AuditEntry` receives an **independent copy** of the `metadata` dict so
  mutations on one entry do not affect others.
