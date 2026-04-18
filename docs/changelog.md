# Changelog

The `changelog` subcommand lets you record and review schema changes over time.

## Recording a change

After diffing two schemas, record the result into a persistent changelog file:

```bash
streamdiff changelog record old.json new.json --stream my-topic
```

This appends an entry to `.streamdiff/changelog.json` (configurable via `--changelog`).

## Viewing the changelog

```bash
streamdiff changelog show
```

Output (text):

```
[2024-06-01T12:00:00Z] my-topic
  + new_field
  - old_field (BREAKING)
```

### JSON output

```bash
streamdiff changelog show --json
```

### Filter to breaking changes only

```bash
streamdiff changelog show --breaking-only
```

## Entry format

Each entry in the JSON file contains:

| Field       | Type     | Description                        |
|-------------|----------|------------------------------------|
| `timestamp` | string   | ISO-8601 UTC timestamp             |
| `stream`    | string   | Stream name label                  |
| `breaking`  | boolean  | Whether any breaking changes exist |
| `added`     | string[] | Names of added fields              |
| `removed`   | string[] | Names of removed fields            |
| `modified`  | string[] | Names of type-changed fields       |

## Custom changelog path

```bash
streamdiff changelog record old.json new.json --changelog /var/log/schema-changelog.json
```
