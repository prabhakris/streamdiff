"""compactor.py – collapse a list of SchemaChanges into a minimal representative set.

When multiple changes affect the same field (e.g. a remove followed by an add
with a different type), the compactor merges them into the single most-severe
change so downstream reporters don't double-count.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Tuple

from streamdiff.diff import SchemaChange, ChangeType, DiffResult


# Priority order – higher index wins when two changes collide on the same field.
_PRIORITY: Dict[ChangeType, int] = {
    ChangeType.ADDED: 0,
    ChangeType.REMOVED: 1,
    ChangeType.TYPE_CHANGED: 2,
}


@dataclass
class CompactResult:
    original_count: int
    compacted: List[SchemaChange] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(self.compacted)

    def to_dict(self) -> dict:
        return {
            "original_count": self.original_count,
            "compacted_count": len(self.compacted),
            "changes": [
                {"field": c.field_name, "change_type": c.change_type.value}
                for c in self.compacted
            ],
        }

    def __str__(self) -> str:
        if not self.compacted:
            return "CompactResult(no changes)"
        lines = [f"CompactResult({len(self.compacted)} of {self.original_count} changes):"]
        for c in self.compacted:
            lines.append(f"  {c.field_name}: {c.change_type.value}")
        return "\n".join(lines)


def _change_key(change: SchemaChange) -> str:
    """Return the grouping key for a change (field name)."""
    return change.field_name


def _higher_priority(a: SchemaChange, b: SchemaChange) -> SchemaChange:
    """Return whichever change has the higher severity priority."""
    pa = _PRIORITY.get(a.change_type, -1)
    pb = _PRIORITY.get(b.change_type, -1)
    return a if pa >= pb else b


def compact_changes(changes: List[SchemaChange]) -> CompactResult:
    """Collapse *changes* so each field name appears at most once."""
    original_count = len(changes)
    seen: Dict[str, SchemaChange] = {}
    for change in changes:
        key = _change_key(change)
        if key in seen:
            seen[key] = _higher_priority(seen[key], change)
        else:
            seen[key] = change
    return CompactResult(original_count=original_count, compacted=list(seen.values()))


def compact_result(diff: DiffResult) -> CompactResult:
    """Convenience wrapper that compacts the changes inside a *DiffResult*."""
    return compact_changes(diff.changes)
