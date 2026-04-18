"""Schema pinning: mark a schema version as a known-good pin and compare against it."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Optional

from streamdiff.schema import StreamSchema
from streamdiff.diff import DiffResult, compute_diff

PINS_DIR = ".streamdiff_pins"


def pin_path(name: str, pins_dir: str = PINS_DIR) -> str:
    return os.path.join(pins_dir, f"{name}.json")


def save_pin(name: str, schema: StreamSchema, pins_dir: str = PINS_DIR) -> str:
    os.makedirs(pins_dir, exist_ok=True)
    path = pin_path(name, pins_dir)
    data = {
        "name": schema.name,
        "fields": [
            {"name": f.name, "type": f.field_type.value, "required": f.required}
            for f in schema.fields
        ],
    }
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)
    return path


def load_pin(name: str, pins_dir: str = PINS_DIR) -> Optional[StreamSchema]:
    path = pin_path(name, pins_dir)
    if not os.path.exists(path):
        return None
    from streamdiff.loader import _parse_schema
    with open(path) as fh:
        data = json.load(fh)
    return _parse_schema(data)


def list_pins(pins_dir: str = PINS_DIR) -> list[str]:
    if not os.path.isdir(pins_dir):
        return []
    return [f[:-5] for f in os.listdir(pins_dir) if f.endswith(".json")]


def delete_pin(name: str, pins_dir: str = PINS_DIR) -> bool:
    path = pin_path(name, pins_dir)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


@dataclass
class PinCompareResult:
    pin_name: str
    found: bool
    diff: Optional[DiffResult] = field(default=None)

    def __bool__(self) -> bool:
        return self.found


def compare_to_pin(name: str, current: StreamSchema, pins_dir: str = PINS_DIR) -> PinCompareResult:
    pinned = load_pin(name, pins_dir)
    if pinned is None:
        return PinCompareResult(pin_name=name, found=False)
    diff = compute_diff(pinned, current)
    return PinCompareResult(pin_name=name, found=True, diff=diff)
