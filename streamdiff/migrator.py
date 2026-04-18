"""Generate migration hints from schema diff results."""
from dataclasses import dataclass, field
from typing import List
from streamdiff.diff import SchemaChange, ChangeType, DiffResult


@dataclass
class MigrationHint:
    change: SchemaChange
    hint: str
    example: str = ""

    def __str__(self) -> str:
        parts = [f"[{self.change.change_type.value}] {self.change.field_name}: {self.hint}"]
        if self.example:
            parts.append(f"  example: {self.example}")
        return "\n".join(parts)


def _hint_for(change: SchemaChange) -> MigrationHint:
    name = change.field_name
    ct = change.change_type

    if ct == ChangeType.ADDED:
        req = getattr(change.new_field, "required", False)
        if req:
            hint = f"Add required field '{name}' to all producers before deploying consumers."
            example = f'"{name}": <value>  # required'
        else:
            hint = f"Add optional field '{name}'; existing consumers can ignore it safely."
            example = f'"{name}": null  # optional'
    elif ct == ChangeType.REMOVED:
        hint = f"Remove all reads of '{name}' from consumers before dropping it from producers."
        example = f"# delete field '{name}' from schema and producer code"
    elif ct == ChangeType.TYPE_CHANGED:
        old = change.old_field.field_type.value if change.old_field else "?"
        new = change.new_field.field_type.value if change.new_field else "?"
        hint = f"Migrate '{name}' from {old} to {new}; update producers and consumers atomically."
        example = f"cast({name}, {new})"
    else:
        hint = f"Review change to '{name}'."
        example = ""

    return MigrationHint(change=change, hint=hint, example=example)


def build_hints(result: DiffResult) -> List[MigrationHint]:
    return [_hint_for(c) for c in result.changes]


def format_hints_text(hints: List[MigrationHint]) -> str:
    if not hints:
        return "No migration steps required."
    lines = ["Migration hints:", ""]
    for h in hints:
        lines.append(str(h))
        lines.append("")
    return "\n".join(lines).rstrip()


def format_hints_dict(hints: List[MigrationHint]) -> List[dict]:
    return [
        {
            "field": h.change.field_name,
            "change_type": h.change.change_type.value,
            "hint": h.hint,
            "example": h.example,
        }
        for h in hints
    ]
