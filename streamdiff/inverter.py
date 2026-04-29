"""Invert a schema diff: swap added/removed, keep type-changed as-is."""
from dataclasses import dataclass
from typing import List

from streamdiff.diff import ChangeType, SchemaChange, DiffResult


@dataclass
class InvertResult:
    changes: List[SchemaChange]

    def __bool__(self) -> bool:
        return bool(self.changes)

    def to_dict(self) -> dict:
        return {
            "changes": [
                {
                    "field": c.field_name,
                    "change_type": c.change_type.value,
                    "old_type": c.old_type.value if c.old_type else None,
                    "new_type": c.new_type.value if c.new_type else None,
                }
                for c in self.changes
            ],
            "total": len(self.changes),
        }

    def __str__(self) -> str:
        if not self.changes:
            return "InvertResult(no changes)"
        parts = [f"{c.change_type.value}:{c.field_name}" for c in self.changes]
        return f"InvertResult({', '.join(parts)})"


def _invert_change(change: SchemaChange) -> SchemaChange:
    """Return a new SchemaChange with ADDED<->REMOVED swapped."""
    if change.change_type == ChangeType.ADDED:
        return SchemaChange(
            field_name=change.field_name,
            change_type=ChangeType.REMOVED,
            old_type=change.new_type,
            new_type=None,
        )
    if change.change_type == ChangeType.REMOVED:
        return SchemaChange(
            field_name=change.field_name,
            change_type=ChangeType.ADDED,
            old_type=None,
            new_type=change.old_type,
        )
    # TYPE_CHANGED: swap old/new types
    return SchemaChange(
        field_name=change.field_name,
        change_type=change.change_type,
        old_type=change.new_type,
        new_type=change.old_type,
    )


def invert_diff(result: DiffResult) -> InvertResult:
    """Invert all changes in a DiffResult."""
    inverted = [_invert_change(c) for c in result.changes]
    return InvertResult(changes=inverted)
