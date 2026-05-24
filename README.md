# sqlsift

A Python library for diffing query result sets and surfacing row-level discrepancies in data migrations.

---

## Installation

```bash
pip install sqlsift
```

---

## Usage

```python
from sqlsift import ResultSetDiff

# Two query result sets as lists of dicts
source = [
    {"id": 1, "name": "Alice", "balance": 100.0},
    {"id": 2, "name": "Bob",   "balance": 200.0},
]

target = [
    {"id": 1, "name": "Alice", "balance": 105.0},
    {"id": 3, "name": "Carol", "balance": 300.0},
]

diff = ResultSetDiff(source, target, key="id")

print(diff.summary())
# Modified rows : 1
# Missing rows  : 1  (in source, not in target)
# Added rows    : 1  (in target, not in source)

for change in diff.changes():
    print(change)
# RowChange(key=1, field='balance', source=100.0, target=105.0)
# MissingRow(key=2, row={'id': 2, 'name': 'Bob', 'balance': 200.0})
# AddedRow(key=3, row={'id': 3, 'name': 'Carol', 'balance': 300.0})
```

Export discrepancies to a report:

```python
diff.to_csv("discrepancies.csv")
diff.to_json("discrepancies.json")
```

---

## Features

- Key-based row matching across two result sets
- Field-level diff with type-aware comparison
- CSV and JSON export for audit trails
- Works with any data source — databases, CSVs, DataFrames

---

## License

MIT © sqlsift contributors