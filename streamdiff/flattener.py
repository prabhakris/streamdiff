"""Flatten nested StreamSchema fields into dot-notation paths."""
from dataclasses import dataclass, field
from typing import Dict, List
from streamdiff.schema import SchemaField, StreamSchema, FieldType


@dataclass
class FlatField:
    path: str
    field_type: FieldType
    required: bool

    def to_dict(self) -> dict:
        return {"path": self.path, "type": self.field_type.value, "required": self.required}

    def __str__(self) -> str:
        req = "required" if self.required else "optional"
        return f"{self.path} ({self.field_type.value}, {req})"


@dataclass
class FlatSchema:
    name: str
    fields: List[FlatField] = field(default_factory=list)

    def by_path(self) -> Dict[str, FlatField]:
        return {f.path: f for f in self.fields}

    def to_dict(self) -> dict:
        return {"name": self.name, "fields": [f.to_dict() for f in self.fields]}


def _flatten_fields(
    fields: List[SchemaField], prefix: str = "", separator: str = "."
) -> List[FlatField]:
    result = []
    for f in fields:
        path = f"{prefix}{separator}{f.name}" if prefix else f.name
        result.append(FlatField(path=path, field_type=f.field_type, required=f.required))
        if hasattr(f, "children") and f.children:
            result.extend(_flatten_fields(f.children, prefix=path, separator=separator))
    return result


def flatten_schema(schema: StreamSchema, separator: str = ".") -> FlatSchema:
    flat_fields = _flatten_fields(list(schema.fields.values()), separator=separator)
    return FlatSchema(name=schema.name, fields=flat_fields)


def diff_flat_schemas(old: FlatSchema, new: FlatSchema) -> dict:
    old_map = old.by_path()
    new_map = new.by_path()
    added = [p for p in new_map if p not in old_map]
    removed = [p for p in old_map if p not in new_map]
    changed = [
        p for p in old_map
        if p in new_map and old_map[p].field_type != new_map[p].field_type
    ]
    return {"added": added, "removed": removed, "type_changed": changed}
