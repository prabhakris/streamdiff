# Grouping Changes

`streamdiff` can group detected schema changes to give a high-level summary
of which namespaces or change categories are affected.

## Options

| Flag | Values | Description |
|------|--------|-------------|
| `--group-by` | `prefix`, `change_type` | Group changes before printing summary |
| `--group-separator` | any string (default `.`) | Separator used to split field names when grouping by prefix |

## Group by prefix

Fields are split on the separator and the first segment is used as the group key.

```bash
streamdiff old.json new.json --group-by prefix
```

Example output:

```
  [order] 1 change(s)
  [user] 3 change(s)
```

## Group by change type

```bash
streamdiff old.json new.json --group-by change_type
```

Example output:

```
  [added] 2 change(s)
  [removed] 1 change(s)
  [type_changed] 1 change(s)
```

## Custom separator

For Avro-style namespaced fields using `/`:

```bash
streamdiff old.json new.json --group-by prefix --group-separator /
```
