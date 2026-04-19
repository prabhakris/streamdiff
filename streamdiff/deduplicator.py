"""Deduplicator: remove duplicate SchemaChange entries from a DiffResult."""
from dataclasses import dataclass, field
from typing import List

from streamdiff.diff import DiffResult, SchemaChange


@dataclass
class DeduplicateResult:
    kept: List[SchemaChange] = field(default_factory=list)
    removed: List[SchemaChange] = field(default_factory=list)

    def __bool__(self) -> bool:
        return len(self.removed) > 0

    def to_dict(self) -> dict:
        return {
            "kept": len(self.kept),
            "removed": len(self.removed),
            "changes": [
                {"field": c.field_name, "change_type": c.change_type.value}
                for c in self.kept
            ],
        }

    def __str__(self) -> str:
        if not self.removed:
            return "No duplicates found."
        return (
            f"Removed {len(self.removed)} duplicate(s); "
            f"{len(self.kept)} unique change(s) kept."
        )


def _change_key(change: SchemaChange) -> tuple:
    """Unique key identifying a change."""
    return (change.field_name, change.change_type)


def deduplicate(result: DiffResult) -> DeduplicateResult:
    """Return a DeduplicateResult with duplicate SchemaChanges removed."""
    seen = set()
    kept: List[SchemaChange] = []
    removed: List[SchemaChange] = []

    for change in result.changes:
        key = _change_key(change)
        if key in seen:
            removed.append(change)
        else:
            seen.add(key)
            kept.append(change)

    return DeduplicateResult(kept=kept, removed=removed)


def deduplicate_into_result(result: DiffResult) -> DiffResult:
    """Return a new DiffResult with duplicates stripped."""
    dedup = deduplicate(result)
    return DiffResult(changes=dedup.kept)
