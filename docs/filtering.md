# Filtering Changes

`streamdiff` lets you narrow the diff output using filter flags so you only see the changes that matter.

## Available Flags

| Flag | Description |
|------|-------------|
| `--field NAME` | Show changes for a single field by name. |
| `--change-type TYPE` | Limit to `added`, `removed`, or `type_changed`. |
| `--breaking-only` | Show only breaking changes. |
| `--include-fields a,b` | Comma-separated allow-list of field names. |
| `--exclude-fields a,b` | Comma-separated deny-list of field names. |

## Examples

```bash
# Only breaking changes
streamdiff old.json new.json --breaking-only

# Only changes to the 'user_id' field
streamdiff old.json new.json --field user_id

# Only added fields
streamdiff old.json new.json --change-type added

# Include only specific fields
streamdiff old.json new.json --include-fields user_id,email

# Exclude noisy fields
streamdiff old.json new.json --exclude-fields updated_at,created_at
```

## Combining Filters

Filters are applied in order:
1. `--field` / `--change-type` / `--breaking-only`
2. `--include-fields`
3. `--exclude-fields`

All active filters are ANDed together.
