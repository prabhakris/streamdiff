"""Generate and persist a human-readable changelog from diff results."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from streamdiff.diff import DiffResult, ChangeType


@dataclass
class ChangelogEntry:
    timestamp: str
    stream: str
    breaking: bool
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    modified: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "stream": self.stream,
            "breaking": self.breaking,
            "added": self.added,
            "removed": self.removed,
            "modified": self.modified,
        }

    def to_text(self) -> str:
        lines = [f"[{self.timestamp}] {self.stream} {'(BREAKING)' if self.breaking else ''}".strip()]
        for name in self.added:
            lines.append(f"  + {name}")
        for name in self.removed:
            lines.append(f"  - {name}")
        for name in self.modified:
            lines.append(f"  ~ {name}")
        if not (self.added or self.removed or self.modified):
            lines.append("  (no changes)")
        return "\n".join(lines)


def build_entry(result: DiffResult, stream: str = "unknown") -> ChangelogEntry:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    added, removed, modified = [], [], []
    for c in result.changes:
        if c.change_type == ChangeType.ADDED:
            added.append(c.field_name)
        elif c.change_type == ChangeType.REMOVED:
            removed.append(c.field_name)
        else:
            modified.append(c.field_name)
    from streamdiff.diff import has_breaking_changes
    return ChangelogEntry(
        timestamp=ts,
        stream=stream,
        breaking=has_breaking_changes(result),
        added=added,
        removed=removed,
        modified=modified,
    )


def append_changelog(entry: ChangelogEntry, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing: List[dict] = []
    if path.exists():
        existing = json.loads(path.read_text())
    existing.append(entry.to_dict())
    path.write_text(json.dumps(existing, indent=2))


def load_changelog(path: Path) -> List[ChangelogEntry]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text())
    return [
        ChangelogEntry(
            timestamp=r["timestamp"],
            stream=r["stream"],
            breaking=r["breaking"],
            added=r.get("added", []),
            removed=r.get("removed", []),
            modified=r.get("modified", []),
        )
        for r in raw
    ]
