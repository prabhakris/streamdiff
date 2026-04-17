# Schema Snapshots

Streamdiff can save named snapshots of a schema and compare future schemas against them. This is useful for tracking baseline schemas in CI or across deployments.

## Saving a Snapshot

```bash
streamdiff snapshot save schemas/orders.json v1.0
```

The snapshot is saved under `.streamdiff_snapshots/v1.0.json` by default.

Use `--dir` to specify a custom directory:

```bash
streamdiff snapshot save schemas/orders.json v1.0 --dir .snapshots
```

## Comparing Against a Snapshot

```bash
streamdiff snapshot compare schemas/orders.json v1.0
```

This loads the saved snapshot as the baseline and diffs it against the provided schema file. The exit code follows the same convention as the main `diff` command:

- `0` — no changes or only safe changes
- `1` — breaking changes detected

### JSON output

```bash
streamdiff snapshot compare schemas/orders.json v1.0 --json
```

## Listing Snapshots

```bash
streamdiff snapshot list
```

Outputs the names of all saved snapshots in the default directory.

## Deleting a Snapshot

```bash
streamdiff snapshot delete v1.0
```

## Snapshot File Format

Snapshots are plain JSON files and can be committed to version control:

```json
{
  "saved_at": "2024-06-01T12:00:00+00:00",
  "name": "v1.0",
  "metadata": {},
  "fields": [
    {"name": "id", "type": "string", "required": true},
    {"name": "amount", "type": "double", "required": false}
  ]
}
```
