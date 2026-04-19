# Schema Resolver

The `resolve` subcommand merges field definitions from multiple named schema files and detects type conflicts between them.

## Usage

```bash
streamdiff resolve NAME1:schema1.json NAME2:schema2.json [options]
```

### Arguments

| Argument | Description |
|---|---|
| `NAME:FILE` | One or more named schema files. The name is used to identify the source of each field. |

### Options

| Flag | Description |
|---|---|
| `--json` | Output result as JSON |
| `--strict` | Exit with code `1` if any conflicts are found |

## Examples

### Merge two schemas

```bash
streamdiff resolve common:common.json events:events.json
```

Output:
```
Resolved 5 field(s) from 2 schema(s).
  id (required) from 'common'
  timestamp (required) from 'common'
  event_type (required) from 'events'
  ...
```

### Detect conflicts

If the same field name appears in two schemas with different types, a conflict is reported:

```
1 conflict(s) found:
  ! Field 'count' type conflict: 'common' has int, 'events' has string
```

### JSON output

```bash
streamdiff resolve a:a.json b:b.json --json
```

```json
{
  "resolved": [
    {"name": "id", "source": "a", "type": "string", "required": true}
  ],
  "conflicts": []
}
```

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success (or conflicts found but `--strict` not set) |
| `1` | Conflicts found and `--strict` is enabled |
| `2` | Bad arguments or file not found |
