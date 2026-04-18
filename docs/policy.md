# Policy Enforcement

`streamdiff` supports policy enforcement to gate schema changes based on configurable rules.

## Overview

A **policy** defines what kinds of schema changes are acceptable. When a diff is evaluated against a policy, any change that violates the policy produces a **violation**. If violations exist, the CLI exits with code `1`.

## CLI Usage

```bash
# Fail on any breaking change (default)
streamdiff diff old.json new.json --policy-name strict

# Allow breaking changes but block removals explicitly
streamdiff diff old.json new.json --allow-breaking --block-types removed

# Output violations as JSON
streamdiff diff old.json new.json --policy-json
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--policy-name` | `default` | Label for the policy |
| `--allow-breaking` | `false` | Skip severity-based breaking check |
| `--block-types` | `[]` | Explicitly blocked change types |
| `--policy-json` | `false` | Emit violations as JSON |

## Change Types

Valid values for `--block-types`:
- `added`
- `removed`
- `type_changed`
- `required_changed`

## Python API

```python
from streamdiff.policy import PolicyRule, evaluate_policy

rule = PolicyRule(
    name="no-removals",
    description="Removals are never allowed",
    allow_breaking=False,
    blocked_change_types=[ChangeType.REMOVED],
)

result = evaluate_policy(rule, diff_result)
if not result.passed:
    for v in result.violations:
        print(v)
```

## Exit Codes

- `0` — policy passed
- `1` — one or more violations found
