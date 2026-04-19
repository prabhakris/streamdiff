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

# Lookup a single field by exact name
entry = idx.get("user_id")

# Search fields whose name contains a substring (case-insensitive)
matches = idx.search("user")

# Filter by type
from streamdiff.schema import FieldType
strings = idx.by_type(FieldType.STRING)

# Filter by depth
top_level = idx.by_depth(0)
nested = idx.by_depth(2)
```

### `idx.by_depth(depth)`

Returns all index entries whose field depth equals `depth`.
Useful for inspecting only top-level fields (`depth=0`) or a specific
nesting level without manually filtering on `.` counts.

```python
# List all top-level field names
top_names = [e.name for e in idx.by_depth(0)]
```

## Field depth

Depth is determined by counting `.` separators in the field name.
A top-level field like `user_id` has depth `0`; `user.address.city` has depth `2`.
