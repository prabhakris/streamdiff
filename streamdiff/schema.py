"""Schema representation and diffing for Kafka and Kinesis streams."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FieldType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    NULL = "null"


@dataclass
class SchemaField:
    name: str
    type: FieldType
    required: bool = True
    nullable: bool = False
    description: str = ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SchemaField):
            return False
        return (
            self.name == other.name
            and self.type == other.type
            and self.required == other.required
            and self.nullable == other.nullable
        )


@dataclass
class StreamSchema:
    name: str
    version: str
    fields: list[SchemaField] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def field_map(self) -> dict[str, SchemaField]:
        return {f.name: f for f in self.fields}


@dataclass
class SchemaDiff:
    added: list[SchemaField] = field(default_factory=list)
    removed: list[SchemaField] = field(default_factory=list)
    modified: list[tuple[SchemaField, SchemaField]] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)

    @property
    def is_breaking(self) -> bool:
        """Removals and required additions are breaking changes."""
        if self.removed:
            return True
        if any(f.required for f in self.added):
            return True
        for old, new in self.modified:
            if old.type != new.type or (not old.required and new.required):
                return True
        return False


def diff_schemas(old: StreamSchema, new: StreamSchema) -> SchemaDiff:
    """Compute the diff between two stream schemas."""
    old_fields = old.field_map()
    new_fields = new.field_map()

    added = [f for name, f in new_fields.items() if name not in old_fields]
    removed = [f for name, f in old_fields.items() if name not in new_fields]
    modified = [
        (old_fields[name], new_fields[name])
        for name in old_fields
        if name in new_fields and old_fields[name] != new_fields[name]
    ]

    return SchemaDiff(added=added, removed=removed, modified=modified)
