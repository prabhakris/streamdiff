# Labeler

The `labeler` module attaches human-readable labels to each detected schema change, making it easier to understand the impact at a glance.

## Labels

| Change Type   | Labels Assigned                        |
|---------------|----------------------------------------|
| Added optional| `additive`, `safe`                     |
| Added required| `additive`, `breaking`                 |
| Removed       | `destructive`, `breaking`              |
| Type changed  | `structural`, `breaking`               |

## Python API

```python
from streamdiff.labeler import build_label_report

report = build_label_report(diff_result.changes)
for lc in report.labeled:
    print(lc)  # field_name [label1, label2]
```

Add custom labels to every change:

```python
report = build_label_report(diff_result.changes, extra=["reviewed", "approved"])
```

Export as dict:

```python
print(report.to_dict())
```

## CLI Usage

```bash
# Print labeled changes
streamdiff diff old.json new.json --label

# Output as JSON
streamdiff diff old.json new.json --label-json

# Attach extra labels
streamdiff diff old.json new.json --label --extra-labels reviewed approved
```

## Output Example

```
user_id [additive, safe]
email [destructive, breaking]
age [structural, breaking]
```
