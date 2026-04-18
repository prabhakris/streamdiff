# Schema Profiler

The `profile` command analyses a single schema file and reports field-level statistics without requiring a second schema to compare against.

## Usage

```bash
streamdiff profile path/to/schema.json
streamdiff profile path/to/schema.json --json
streamdiff profile path/to/schema.json --min-depth 2
```

## Output (text)

```
Schema : orders_v3
Fields : 12
Required / Optional: 8 / 4
Max depth : 3
Type breakdown:
  boolean: 1
  int: 3
  string: 8
Fields:
  id (int, required, depth=1)
  customer.address.zip (string, optional, depth=3)
  ...
```

## Output (JSON)

Pass `--json` to receive a machine-readable object:

```json
{
  "schema_name": "orders_v3",
  "total_fields": 12,
  "required_count": 8,
  "optional_count": 4,
  "type_counts": {"string": 8, "int": 3, "boolean": 1},
  "max_depth": 3,
  "fields": [
    {"name": "id", "type": "int", "required": true, "depth": 1}
  ]
}
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--json` | false | Emit JSON instead of plain text |
| `--min-depth N` | 0 | Only list fields nested at depth ≥ N |

## Exit codes

`profile` always exits `0` — it is a read-only inspection command.
