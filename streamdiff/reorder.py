"""Detect and report field ordering changes between two schemas."""

from dataclasses import dataclass, field
from typing import List, Optional
from streamdiff.schema import StreamSchema


@dataclass
class ReorderChange:
    field_name: str
    old_index: int
    new_index: int

    def to_dict(self) -> dict:
        return {
            "field": self.field_name,
            "old_index": self.old_index,
            "new_index": self.new_index,
        }

    def __str__(self) -> str:
        return (
            f"{self.field_name}: position {self.old_index} -> {self.new_index}"
        )


@dataclass
class ReorderResult:
    changes: List[ReorderChange] = field(default_factory=list)
    old_order: List[str] = field(default_factory=list)
    new_order: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return len(self.changes) > 0

    def to_dict(self) -> dict:
        return {
            "reordered": [c.to_dict() for c in self.changes],
            "old_order": self.old_order,
            "new_order": self.new_order,
        }

    def __str__(self) -> str:
        if not self.changes:
            return "No field order changes."
        lines = [str(c) for c in self.changes]
        return "Field order changes:\n" + "\n".join(f"  {l}" for l in lines)


def detect_reorder(old: StreamSchema, new: StreamSchema) -> ReorderResult:
    """Compare field ordering between old and new schema.

    Only fields present in both schemas are considered; added or removed
    fields are ignored for ordering purposes.
    """
    old_names = [f.name for f in old.fields]
    new_names = [f.name for f in new.fields]

    common_old = [n for n in old_names if n in set(new_names)]
    common_new = [n for n in new_names if n in set(old_names)]

    old_index = {name: i for i, name in enumerate(common_old)}
    new_index = {name: i for i, name in enumerate(common_new)}

    changes = [
        ReorderChange(
            field_name=name,
            old_index=old_index[name],
            new_index=new_index[name],
        )
        for name in common_old
        if old_index[name] != new_index[name]
    ]

    return ReorderResult(
        changes=changes,
        old_order=old_names,
        new_order=new_names,
    )
