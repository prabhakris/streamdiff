# Schema Watchdog

The `watch` subcommand polls a schema file at a configurable interval and
reports any changes as they are detected.

## Basic usage

```bash
streamdiff watch path/to/schema.json
```

By default the file is checked every **5 seconds**. Use `--interval` to change
this:

```bash
streamdiff watch path/to/schema.json --interval 10
```

## Output format

Text output (default):

```bash
streamdiff watch schema.json --format text
```

JSON output (useful for piping into other tools):

```bash
streamdiff watch schema.json --format json
```

## Exiting on breaking changes

Pass `--break-on-breaking` to make the process exit with code `1` the moment a
breaking change is detected:

```bash
streamdiff watch schema.json --break-on-breaking
```

This is useful in CI pipelines where a long-running process monitors a live
schema registry endpoint via a local proxy file.

## Programmatic API

```python
from streamdiff.watchdog import WatchConfig, watch

def on_change(event):
    print(f"Change detected at iteration {event.iteration}")
    for c in event.result.changes:
        print(" ", c)

cfg = WatchConfig(
    schema_path="schema.json",
    interval=2.0,
    on_change=on_change,
)
watch(cfg)
```

## Stopping the watcher

Press `Ctrl-C` to stop. The CLI handles `KeyboardInterrupt` gracefully and
exits with code `0`.
