"""Poll a schema source and emit diffs when changes are detected."""

import time
from dataclasses import dataclass, field
from typing import Callable, Optional

from streamdiff.diff import DiffResult, diff_schemas
from streamdiff.loader import load_schema
from streamdiff.schema import StreamSchema


@dataclass
class WatchEvent:
    previous: StreamSchema
    current: StreamSchema
    result: DiffResult
    iteration: int


@dataclass
class WatchConfig:
    schema_path: str
    interval: float = 5.0
    max_iterations: Optional[int] = None
    on_change: Callable[[WatchEvent], None] = field(default=lambda e: None)
    on_breaking: Callable[[WatchEvent], None] = field(default=lambda e: None)


def _load(path: str) -> StreamSchema:
    return load_schema(path)


def watch(config: WatchConfig) -> None:
    """Continuously poll schema_path and invoke callbacks on changes."""
    current = _load(config.schema_path)
    iteration = 0

    while True:
        if config.max_iterations is not None and iteration >= config.max_iterations:
            break

        time.sleep(config.interval)
        iteration += 1

        try:
            updated = _load(config.schema_path)
        except Exception:
            continue

        result = diff_schemas(current, updated)
        if result.changes:
            event = WatchEvent(
                previous=current,
                current=updated,
                result=result,
                iteration=iteration,
            )
            config.on_change(event)
            if result.has_breaking:
                config.on_breaking(event)

        current = updated
