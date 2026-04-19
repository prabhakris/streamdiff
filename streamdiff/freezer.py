"""Freeze a schema to a locked snapshot that blocks any future changes."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from streamdiff.schema import StreamSchema
from streamdiff.diff import DiffResult, SchemaChange


@dataclass
class FreezeRecord:
    name: str
    path: str
    fields: List[str]

    def to_dict(self) -> dict:
        return {"name": self.name, "path": self.path, "fields": self.fields}

    def __str__(self) -> str:
        return f"FreezeRecord({self.name}, {len(self.fields)} fields)"


@dataclass
class FreezeViolation:
    field_name: str
    reason: str

    def __str__(self) -> str:
        return f"[FROZEN] {self.field_name}: {self.reason}"


@dataclass
class FreezeResult:
    record: FreezeRecord
    violations: List[FreezeViolation] = field(default_factory=list)

    def ok(self) -> bool:
        return len(self.violations) == 0

    def to_dict(self) -> dict:
        return {
            "record": self.record.to_dict(),
            "ok": self.ok(),
            "violations": [str(v) for v in self.violations],
        }


def freeze_path(directory: str, name: str) -> Path:
    return Path(directory) / f"{name}.freeze.json"


def save_freeze(schema: StreamSchema, name: str, directory: str) -> FreezeRecord:
    path = freeze_path(directory, name)
    Path(directory).mkdir(parents=True, exist_ok=True)
    fields = sorted(schema.field_map.keys())
    record = FreezeRecord(name=name, path=str(path), fields=fields)
    path.write_text(json.dumps(record.to_dict(), indent=2))
    return record


def load_freeze(name: str, directory: str) -> Optional[FreezeRecord]:
    path = freeze_path(directory, name)
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return FreezeRecord(name=data["name"], path=data["path"], fields=data["fields"])


def check_freeze(record: FreezeRecord, diff: DiffResult) -> FreezeResult:
    violations: List[FreezeViolation] = []
    frozen = set(record.fields)
    for change in diff.changes:
        if change.field_name in frozen:
            violations.append(FreezeViolation(
                field_name=change.field_name,
                reason=f"field is frozen but has change: {change.change_type.value}",
            ))
    return FreezeResult(record=record, violations=violations)
