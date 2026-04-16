from dataclasses import dataclass
from enum import Enum
from typing import List

from streamdiff.schema import StreamSchema


class ChangeType(str, Enum):
    ADDED_OPTIONAL = "added_optional"
    ADDED_REQUIRED = "added_required"
    REMOVED = "removed"
    TYPE_CHANGED = "type_changed"
    NULLABILITY_CHANGED = "nullability_changed"


@dataclass
class SchemaChange:
    field_name: str
    change_type: ChangeType
    detail: str = ""

    @property
    def is_breaking(self) -> bool:
        return self.change_type in (
            ChangeType.ADDED_REQUIRED,
            ChangeType.REMOVED,
            ChangeType.TYPE_CHANGED,
        )


@dataclass
class DiffResult:
    changes: List[SchemaChange]

    @property
    def has_breaking_changes(self) -> bool:
        return any(c.is_breaking for c in self.changes)

    @property
    def breaking_changes(self) -> List[SchemaChange]:
        return [c for c in self.changes if c.is_breaking]

    @property
    def non_breaking_changes(self) -> List[SchemaChange]:
        return [c for c in self.changes if not c.is_breaking]


def diff_schemas(old: StreamSchema, new: StreamSchema) -> DiffResult:
    changes: List[SchemaChange] = []
    old_fields = old.field_map
    new_fields = new.field_map

    for name, old_field in old_fields.items():
        if name not in new_fields:
            changes.append(SchemaChange(name, ChangeType.REMOVED, f"field '{name}' was removed"))
            continue
        new_field = new_fields[name]
        if old_field.field_type != new_field.field_type:
            changes.append(SchemaChange(
                name, ChangeType.TYPE_CHANGED,
                f"'{name}' type changed from {old_field.field_type} to {new_field.field_type}"
            ))
        if old_field.nullable != new_field.nullable:
            changes.append(SchemaChange(
                name, ChangeType.NULLABILITY_CHANGED,
                f"'{name}' nullability changed from {old_field.nullable} to {new_field.nullable}"
            ))

    for name, new_field in new_fields.items():
        if name not in old_fields:
            if new_field.required:
                changes.append(SchemaChange(
                    name, ChangeType.ADDED_REQUIRED,
                    f"required field '{name}' was added"
                ))
            else:
                changes.append(SchemaChange(
                    name, ChangeType.ADDED_OPTIONAL,
                    f"optional field '{name}' was added"
                ))

    return DiffResult(changes=changes)
