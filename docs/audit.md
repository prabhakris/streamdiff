# Audit Log

`streamdiff` can maintain an append-only audit log of every diff operation,
recording who ran the diff, which schemas were compared, and whether the result
was breaking.

## Recording an entry

Entries are written programmatically via `streamdiff.auditor.record_entry`:

```python
from streamdiff.auditor import record_entry

record_entry(
    old_schema="schemas/v1.json",
    new_schema="schemas/v2.json",
    breaking=True,
    change_count=3,
    user="alice",
    tags=["release", "2.0"],
)
```

Entries are stored as newline-delimited JSON in `.streamdiff/audit/audit.jsonl`.

## CLI

### View the log

```bash
streamdiff audit
```

### View as JSON

```bash
streamdiff audit --json
```

### Filter breaking-only

```bash
streamdiff audit --only-breaking
```

### Limit output

```bash
streamdiff audit --limit 10
```

### Clear the log

```bash
streamdiff audit --clear
```

### Custom audit directory

```bash
streamdiff audit --audit-dir /var/log/streamdiff
```

## Entry fields

| Field | Description |
|---|---|
| `timestamp` | ISO-8601 UTC timestamp |
| `user` | Username (`$USER` env or supplied explicitly) |
| `old_schema` | Path to the old schema file |
| `new_schema` | Path to the new schema file |
| `breaking` | Whether the diff contained breaking changes |
| `change_count` | Total number of detected changes |
| `tags` | Optional list of string tags |
