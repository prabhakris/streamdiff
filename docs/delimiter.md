# Delimiter

The **delimiter** module splits a schema's fields into logical groups based on a separator character found in field names.

This is useful when a flat schema encodes hierarchy through naming conventions such as `user.id`, `user.name`, `order.total`.

## Usage

### Python API

```python
from streamdiff.loader import load_schema
from streamdiff.delimiter import delimit_schema

schema = load_schema("schema.json")
result = delimit_schema(schema, delimiter=".", depth=1)

for prefix, fields in result.chunks.items():
    print(f"{prefix}: {[f.name for f in fields]}")

print(f"Unmatched: {[f.name for f in result.unmatched]}")
```

### CLI

```bash
# Default delimiter (.) and depth 1
streamdiff delimit schema.json

# Custom delimiter
streamdiff delimit schema.json --delimiter _

# Group by two-segment prefix (e.g. a.b.c → group "a.b")
streamdiff delimit schema.json --depth 2

# JSON output
streamdiff delimit schema.json --json
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `delimiter` | `.` | Character used to split field names |
| `depth` | `1` | Number of leading segments used as the group key |

## Output

### Text

```
DelimitResult(delimiter='.', chunks=2, unmatched=1)
  [user]: ['user.id', 'user.name']
  [order]: ['order.id']
  [unmatched]: ['plain']
```

### JSON (`--json`)

```json
{
  "delimiter": ".",
  "original_count": 4,
  "unmatched_count": 1,
  "chunks": {
    "user": [
      {"name": "user.id", "type": "string", "required": true},
      {"name": "user.name", "type": "string", "required": false}
    ],
    "order": [
      {"name": "order.id", "type": "string", "required": true}
    ]
  },
  "unmatched": [
    {"name": "plain", "type": "integer", "required": true}
  ]
}
```

## Notes

- Fields that do not contain the delimiter are placed in `unmatched`.
- Increasing `depth` allows finer-grained grouping for deeply nested naming conventions.
