# Field Indexer

The `index` subcommand builds a searchable in-memory index from a schema file,
allowing quick lookup, filtering, and inspection of fields.

## Usage

```bash
streamdiff index schema.json
streamdiff index schema.json --search user
streamdiff index schema.json --type string
streamdiff index schema.json --required-only
streamdiff index schema.json --json
```

## Options

| Flag | Description |
|------|-------------|
| `--search TEXT` | Filter fields whose name contains TEXT (case-insensitive) |
| `--type TYPE` | Filter by field type (`string`, `int`, `long`, `float`, `double`, `boolean`, `bytes`) |
| `--required-only` | Show only required fields |
| `--json` | Output results as JSON array |

## Output

Default text output:

```
user_id (string, required, depth=0)
user.address.city (string, optional, depth=2)
```

JSON output (`--json`):

```json
[
  {"name": "user_id", "type": "string", "required": true, "depth": 0}
]
```

## Python API

```python
from streamdiff.loader import load_schema
from streamdiff.indexer import build_index

schema = load_schema("schema.json")
idx = build_index(schema)

# Lookup
entry = idx.get("user_id")

# Search
matches = idx.search("user")

# Filter by type
from streamdiff.schema import FieldType
strings = idx.by_type(FieldType.STRING)
```

## Field depth

Depth is determined by counting `.` separators in the field name.
A top-level field like `user_id` has depth `0`; `user.address.city` has depth `2`.
