# Pinpointer

The `pinpoint` command gives detailed, human-readable reasons for every schema change detected between two versions.

## Usage

```bash
streamdiff pinpoint old_schema.json new_schema.json
streamdiff pinpoint old_schema.json new_schema.json --json
```

## Output

Each changed field is printed with:
- **field name**
- **change type** (added, removed, type_changed, required_changed)
- **reason** — a plain-English explanation
- **old/new values** where applicable

### Example

```
email [added]: Field added as optional
count [type_changed]: Field type was modified (int -> string)
score [required_changed]: Field required flag changed (False -> True)
legacy [removed]: Field was removed from schema
```

## JSON output

```json
{
  "pinpoints": [
    {
      "field": "email",
      "change_type": "added",
      "reason": "Field added as optional",
      "old_value": null,
      "new_value": null
    }
  ]
}
```

## Python API

```python
from streamdiff.pinpointer import pinpoint_changes
from streamdiff.diff import compute_diff

result = compute_diff(old_schema, new_schema)
report = pinpoint_changes(result)
for p in report.pinpoints:
    print(p)
```
