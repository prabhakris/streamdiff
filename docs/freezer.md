# Schema Freezer

The **freezer** module lets you lock a schema at a point in time and detect any future modifications to frozen fields.

## Overview

When a schema reaches a stable, production state you can *freeze* it. Any subsequent diff that touches a frozen field is reported as a violation, even if the change would otherwise be considered safe.

## CLI Usage

### Save a freeze record

```bash
streamdiff freeze save schema.json --name v1
```

This writes a freeze record to `.streamdiff/freezes/v1.freeze.json` containing the list of field names present at freeze time.

Options:

| Flag | Default | Description |
|------|---------|-------------|
| `--name` | *(required)* | Logical name for the freeze record |
| `--dir` | `.streamdiff/freezes` | Directory to store freeze records |

### Check against a freeze record

```bash
streamdiff freeze check old.json new.json --name v1
```

Compares the two schemas and reports any changes that touch fields listed in the freeze record.

Options:

| Flag | Default | Description |
|------|---------|-------------|
| `--name` | *(required)* | Freeze record to validate against |
| `--dir` | `.streamdiff/freezes` | Directory containing freeze records |
| `--json` | false | Output result as JSON |

Exit codes:
- `0` — no violations
- `1` — one or more frozen fields were modified
- `2` — error (missing file, unknown freeze record)

## Python API

```python
from streamdiff.freezer import save_freeze, load_freeze, check_freeze
from streamdiff.loader import load_schema
from streamdiff.diff import compute_diff

schema = load_schema("schema.json")
record = save_freeze(schema, name="v1", directory=".streamdiff/freezes")

old = load_schema("old.json")
new = load_schema("new.json")
diff = compute_diff(old, new)

record = load_freeze("v1", ".streamdiff/freezes")
result = check_freeze(record, diff)

if not result.ok():
    for v in result.violations:
        print(v)
```

## Freeze record format

```json
{
  "name": "v1",
  "path": ".streamdiff/freezes/v1.freeze.json",
  "fields": ["id", "name", "created_at"]
}
```
