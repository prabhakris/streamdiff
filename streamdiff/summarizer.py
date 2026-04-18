"""Summarize diff results into human-readable statistics."""
from dataclasses import dataclass, field
from typing import List, Dict
from streamdiff.diff import DiffResult, ChangeType, SchemaChange


@dataclass
class DiffSummary:
    total: int = 0
    added: int = 0
    removed: int = 0
    type_changed: int = 0
    breaking: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)

    def __str__(self) -> str:
        lines = [
            f"Total changes : {self.total}",
            f"  Added       : {self.added}",
            f"  Removed     : {self.removed}",
            f"  Type changed: {self.type_changed}",
            f"  Breaking    : {self.breaking}",
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "added": self.added,
            "removed": self.removed,
            "type_changed": self.type_changed,
            "breaking": self.breaking,
            "by_type": self.by_type,
        }


def _count_by_type(changes: List[SchemaChange]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for c in changes:
        key = c.change_type.value
        counts[key] = counts.get(key, 0) + 1
    return counts


def summarize(result: DiffResult) -> DiffSummary:
    changes = result.changes
    return DiffSummary(
        total=len(changes),
        added=sum(1 for c in changes if c.change_type == ChangeType.ADDED),
        removed=sum(1 for c in changes if c.change_type == ChangeType.REMOVED),
        type_changed=sum(1 for c in changes if c.change_type == ChangeType.TYPE_CHANGED),
        breaking=sum(1 for c in changes if c.is_breaking),
        by_type=_count_by_type(changes),
    )
