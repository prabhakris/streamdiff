"""blender.py — merge two schemas with weighted field selection.

When the same field exists in both schemas, the field from the schema
with the higher weight wins.  Fields that appear in only one schema are
included as-is.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from streamdiff.schema import SchemaField, StreamSchema


@dataclass
class BlendConflict:
    field_name: str
    left_type: str
    right_type: str
    chosen: str  # 'left' | 'right'

    def __str__(self) -> str:
        return (
            f"conflict on '{self.field_name}': "
            f"{self.left_type} vs {self.right_type} → chose {self.chosen}"
        )

    def to_dict(self) -> dict:
        return {
            "field": self.field_name,
            "left_type": self.left_type,
            "right_type": self.right_type,
            "chosen": self.chosen,
        }


@dataclass
class BlendResult:
    schema: StreamSchema
    conflicts: List[BlendConflict] = field(default_factory=list)

    def __bool__(self) -> bool:
        return len(self.conflicts) == 0

    def to_dict(self) -> dict:
        return {
            "fields": [f.name for f in self.schema.fields],
            "conflict_count": len(self.conflicts),
            "conflicts": [c.to_dict() for c in self.conflicts],
        }

    def __str__(self) -> str:
        lines = [f"BlendResult: {len(self.schema.fields)} field(s), {len(self.conflicts)} conflict(s)"]
        for c in self.conflicts:
            lines.append(f"  {c}")
        return "\n".join(lines)


def blend_schemas(
    left: StreamSchema,
    right: StreamSchema,
    left_weight: float = 1.0,
    right_weight: float = 1.0,
) -> BlendResult:
    """Blend *left* and *right* into a single schema.

    When a field exists in both schemas and the types differ, the field
    from the higher-weighted schema wins.  Equal weights favour *left*.
    """
    left_map: Dict[str, SchemaField] = {f.name: f for f in left.fields}
    right_map: Dict[str, SchemaField] = {f.name: f for f in right.fields}

    blended: List[SchemaField] = []
    conflicts: List[BlendConflict] = []

    all_names = list(left_map) + [n for n in right_map if n not in left_map]

    for name in all_names:
        l_field: Optional[SchemaField] = left_map.get(name)
        r_field: Optional[SchemaField] = right_map.get(name)

        if l_field is None:
            blended.append(r_field)  # type: ignore[arg-type]
            continue
        if r_field is None:
            blended.append(l_field)
            continue

        if l_field.field_type == r_field.field_type:
            # Same type — keep the more restrictive (required wins)
            chosen = l_field if (l_field.required or not r_field.required) else r_field
            blended.append(chosen)
        else:
            if right_weight > left_weight:
                winner, chosen_label = r_field, "right"
            else:
                winner, chosen_label = l_field, "left"
            blended.append(winner)
            conflicts.append(
                BlendConflict(
                    field_name=name,
                    left_type=l_field.field_type.value,
                    right_type=r_field.field_type.value,
                    chosen=chosen_label,
                )
            )

    result_schema = StreamSchema(name=left.name or right.name, fields=blended)
    return BlendResult(schema=result_schema, conflicts=conflicts)
