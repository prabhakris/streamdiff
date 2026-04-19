"""Field-level inspection: surface metadata about individual fields across schemas."""
from dataclasses import dataclass, field
from typing import List, Optional
from streamdiff.schema import StreamSchema, SchemaField, FieldType


@dataclass
class FieldInspection:
    name: str
    field_type: FieldType
    required: bool
    present_in_old: bool
    present_in_new: bool

    def status(self) -> str:
        if self.present_in_old and self.present_in_new:
            return "stable"
        if self.present_in_new and not self.present_in_old:
            return "added"
        if self.present_in_old and not self.present_in_new:
            return "removed"
        return "unknown"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.field_type.value,
            "required": self.required,
            "present_in_old": self.present_in_old,
            "present_in_new": self.present_in_new,
            "status": self.status(),
        }

    def __str__(self) -> str:
        req = "required" if self.required else "optional"
        return f"{self.name} ({self.field_type.value}, {req}) [{self.status()}]"


def inspect_field(
    name: str,
    old: Optional[StreamSchema],
    new: Optional[StreamSchema],
) -> Optional[FieldInspection]:
    old_map = old.field_map() if old else {}
    new_map = new.field_map() if new else {}

    old_f: Optional[SchemaField] = old_map.get(name)
    new_f: Optional[SchemaField] = new_map.get(name)

    if old_f is None and new_f is None:
        return None

    src = new_f if new_f is not None else old_f
    return FieldInspection(
        name=name,
        field_type=src.field_type,
        required=src.required,
        present_in_old=old_f is not None,
        present_in_new=new_f is not None,
    )


def inspect_all(
    old: Optional[StreamSchema],
    new: Optional[StreamSchema],
) -> List[FieldInspection]:
    old_map = old.field_map() if old else {}
    new_map = new.field_map() if new else {}
    all_names = sorted(set(old_map) | set(new_map))
    results = []
    for name in all_names:
        ins = inspect_field(name, old, new)
        if ins is not None:
            results.append(ins)
    return results
