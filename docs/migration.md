# Migration Hints

`streamdiff` can generate actionable migration hints for every schema change detected between two versions.

## Overview

When schemas evolve, producers and consumers must be updated in a specific order to avoid data loss or deserialization errors. The migrator module analyses each `SchemaChange` and produces a plain-language hint plus a short code example.

## Change types and hints

| Change | Risk | Suggested order |
|---|---|---|
| Added optional field | Low | Deploy consumers first, then producers |
| Added required field | High | Deploy producers first, then consumers |
| Removed field | High | Remove consumer reads first, then drop from producers |
| Type changed | High | Coordinate producers and consumers atomically |

## Programmatic usage

```python
from streamdiff.loader import load_schema
from streamdiff.diff import diff_schemas
from streamdiff.migrator import build_hints, format_hints_text

old = load_schema("schemas/v1.yaml")
new = load_schema("schemas/v2.yaml")
result = diff_schemas(old, new)
hints = build_hints(result)
print(format_hints_text(hints))
```

## JSON output

```python
from streamdiff.migrator import format_hints_dict
import json

print(json.dumps(format_hints_dict(hints), indent=2))
```

Example output:

```json
[
  {
    "field": "user_id",
    "change_type": "added",
    "hint": "Add required field 'user_id' to all producers before deploying consumers.",
    "example": "\"user_id\": <value>  # required"
  }
]
```

## Integration with CLI

Migration hints are planned for inclusion in the `streamdiff diff --hints` flag in a future release.
