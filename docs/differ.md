# High-Level Differ

The `differ` module provides a single `run_diff` entry point that composes
diff, filtering, severity annotation, and risk scoring into one call.

## Usage

```python
from streamdiff.differ import run_diff, DifferConfig
from streamdiff.severity import Severity
from streamdiff.loader import load_schema

old = load_schema("old.yaml")
new = load_schema("new.yaml")

config = DifferConfig(
    min_severity=Severity.WARNING,
    include_fields=["user_id", "email"],
    score=True,
)

result = run_diff(old, new, config)
print(result.diff.changes)
print(result.risk_score)
print(result.has_breaking)
```

## DifferConfig Options

| Option | Type | Description |
|---|---|---|
| `min_severity` | `Severity` or `None` | Drop changes below this severity |
| `include_fields` | `list[str]` or `None` | Only include named fields |
| `exclude_fields` | `list[str]` or `None` | Exclude named fields |
| `score` | `bool` | Compute and return a `RiskScore` |

## CLI

```bash
streamdiff diff old.yaml new.yaml --score --min-severity warning --include user_id email
```

Flags:
- `--score` — print risk score after the diff summary
- `--min-severity` — one of `info`, `warning`, `error`
- `--include FIELD ...` — whitelist fields
- `--exclude FIELD ...` — blacklist fields
- `--json` — emit JSON output
