"""Annotate schema changes with human-readable descriptions and hints."""

from dataclasses import dataclass
from typing import List

from streamdiff.diff import SchemaChange, ChangeType


@dataclass
class AnnotatedChange:
    change: SchemaChange
    description: str
    hint: str

    def __str__(self) -> str:
        return f"{self.description} — {self.hint}"


_DESCRIPTIONS = {
    ChangeType.ADDED: "Field '{name}' was added ({required})",
    ChangeType.REMOVED: "Field '{name}' was removed",
    ChangeType.TYPE_CHANGED: "Field '{name}' type changed from {old} to {new}",
    ChangeType.REQUIRED_CHANGED: "Field '{name}' required flag changed to {required}",
}

_HINTS = {
    ChangeType.ADDED: "Ensure consumers handle missing values if field is required.",
    ChangeType.REMOVED: "Consumers reading this field will break.",
    ChangeType.TYPE_CHANGED: "Verify consumers can handle the new type.",
    ChangeType.REQUIRED_CHANGED: "Check producer and consumer compatibility.",
}


def _describe(change: SchemaChange) -> str:
    template = _DESCRIPTIONS.get(change.change_type, "Unknown change for '{name}'")
    field = change.new_field or change.old_field
    return template.format(
        name=field.name if field else "?",
        required="required" if (field and field.required) else "optional",
        old=change.old_field.field_type.value if change.old_field else "",
        new=change.new_field.field_type.value if change.new_field else "",
    )


def annotate(change: SchemaChange) -> AnnotatedChange:
    return AnnotatedChange(
        change=change,
        description=_describe(change),
        hint=_HINTS.get(change.change_type, ""),
    )


def annotate_all(changes: List[SchemaChange]) -> List[AnnotatedChange]:
    return [annotate(c) for c in changes]
