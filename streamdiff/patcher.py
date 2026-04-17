"""Apply a diff result to a schema to produce a patched schema."""

from typing import List
from streamdiff.schema import StreamSchema, SchemaField
from streamdiff.diff import DiffResult, ChangeType


def apply_patch(base: StreamSchema, result: DiffResult) -> StreamSchema:
    """Return a new StreamSchema with all changes from result applied to base."""
    fields: dict = {name: field for name, field in base.field_map().items()}

    for change in result.changes:
        if change.change_type == ChangeType.ADDED:
            if change.new_field is not None:
                fields[change.field_name] = change.new_field
        elif change.change_type == ChangeType.REMOVED:
            fields.pop(change.field_name, None)
        elif change.change_type == ChangeType.TYPE_CHANGED:
            if change.new_field is not None:
                fields[change.field_name] = change.new_field
        elif change.change_type == ChangeType.NULLABILITY_CHANGED:
            if change.new_field is not None:
                fields[change.field_name] = change.new_field

    return StreamSchema(name=base.name, fields=list(fields.values()))


def patch_summary(result: DiffResult) -> List[str]:
    """Return human-readable lines describing what patch would do."""
    lines = []
    for change in result.changes:
        if change.change_type == ChangeType.ADDED:
            lines.append(f"+ add field '{change.field_name}'")
        elif change.change_type == ChangeType.REMOVED:
            lines.append(f"- remove field '{change.field_name}'")
        elif change.change_type == ChangeType.TYPE_CHANGED:
            old = change.old_field.field_type.value if change.old_field else "?"
            new = change.new_field.field_type.value if change.new_field else "?"
            lines.append(f"~ change type of '{change.field_name}': {old} -> {new}")
        elif change.change_type == ChangeType.NULLABILITY_CHANGED:
            lines.append(f"~ change nullability of '{change.field_name}'")
    if not lines:
        lines.append("no changes to apply")
    return lines
