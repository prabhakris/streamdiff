"""Save and load schema snapshots for baseline comparisons."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Optional

from streamdiff.schema import StreamSchema
from streamdiff.loader import load_schema

_DEFAULT_DIR = ".streamdiff_snapshots"


def snapshot_path(name: str, directory: str = _DEFAULT_DIR) -> str:
    return os.path.join(directory, f"{name}.json")


def save_snapshot(
    schema: StreamSchema,
    name: str,
    directory: str = _DEFAULT_DIR,
    metadata: Optional[dict] = None,
) -> str:
    os.makedirs(directory, exist_ok=True)
    path = snapshot_path(name, directory)
    payload = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "name": name,
        "metadata": metadata or {},
        "fields": [
            {"name": f.name, "type": f.field_type.value, "required": f.required}
            for f in schema.fields
        ],
    }
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=2)
    return path


def load_snapshot(name: str, directory: str = _DEFAULT_DIR) -> StreamSchema:
    path = snapshot_path(name, directory)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Snapshot '{name}' not found at {path}")
    return load_schema(path)


def list_snapshots(directory: str = _DEFAULT_DIR) -> list[str]:
    if not os.path.isdir(directory):
        return []
    return [
        f[:-5]
        for f in sorted(os.listdir(directory))
        if f.endswith(".json")
    ]


def delete_snapshot(name: str, directory: str = _DEFAULT_DIR) -> bool:
    path = snapshot_path(name, directory)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
