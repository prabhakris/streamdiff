# Flattener

The `flattener` module converts a `StreamSchema` into a flat list of fields
using dot-notation paths. This is useful for inspecting deeply nested schemas
or comparing two schemas at the path level.

## Usage

```python
from streamdiff.loader import load_schema
from streamdiff.flattener import flatten_schema, diff_flat_schemas

old = load_schema("old_schema.json")
new = load_schema("new_schema.json")

flat_old = flatten_schema(old)
flat_new = flatten_schema(new)

for f in flat_new.fields:
    print(f)  # e.g. "payload.user.id (string, required)"

diff = diff_flat_schemas(flat_old, flat_new)
print(diff["added"])       # paths added in new
print(diff["removed"])     # paths removed from old
print(diff["type_changed"]) # paths where type changed
```

## CLI

```bash
# Show all flat paths
streamdiff flatten schema.json

# Output as JSON
streamdiff flatten schema.json --json

# Compare two schemas
streamdiff flatten old.json --compare new.json

# Custom separator
streamdiff flatten schema.json --separator /
```

## Output example

```
user_id (string, required)
payload.event_type (string, optional)
payload.timestamp (integer, required)
```

## API

### `flatten_schema(schema, separator=".") -> FlatSchema`
Returns a `FlatSchema` with all fields expanded to dot-notation paths.

### `diff_flat_schemas(old, new) -> dict`
Returns a dict with keys `added`, `removed`, `type_changed` — each a list of paths.

### `FlatField`
Holds `path`, `field_type`, `required`. Supports `.to_dict()` and `str()`.
