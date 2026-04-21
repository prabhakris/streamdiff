"""joiner.py – join two schemas by combining their fields with conflict detection."""
from dataclasses import dataclass, field
from typing import List, Optional
from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class JoinConflict:
    field_name: str
    left_type: str
    right_type: str

    def __str__(self) -> str:
        return (
            f"conflict on '{self.field_name}': "
            f"{self.left_type} vs {self.right_type}"
        )

    def to_dict(self) -> dict:
        return {
            "field": self.field_name,
            "left_type": self.left_type,
            "right_type": self.right_type,
        }


@dataclass
class JoinResult:
    schema: StreamSchema
    conflicts: List[JoinConflict] = field(default_factory=list)
    left_only: List[str] = field(default_factory=list)
    right_only: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return len(self.conflicts) == 0

    def to_dict(self) -> dict:
        return {
            "fields": [f.name for f in self.schema.fields],
            "conflicts": [c.to_dict() for c in self.conflicts],
            "left_only": self.left_only,
            "right_only": self.right_only,
        }

    def __str__(self) -> str:
        lines = [f"JoinResult: {len(self.schema.fields)} field(s)"]
        if self.conflicts:
            lines.append(f"  {len(self.conflicts)} conflict(s):")
            for c in self.conflicts:
                lines.append(f"    - {c}")
        return "\n".join(lines)


def join_schemas(
    left: StreamSchema,
    right: StreamSchema,
    prefer: str = "left",
) -> JoinResult:
    """Combine two schemas. On type conflict, prefer 'left' or 'right'."""
    left_map = {f.name: f for f in left.fields}
    right_map = {f.name: f for f in right.fields}

    all_names = list(left_map) + [n for n in right_map if n not in left_map]

    merged: List[SchemaField] = []
    conflicts: List[JoinConflict] = []
    left_only: List[str] = []
    right_only: List[str] = []

    for name in all_names:
        in_left = name in left_map
        in_right = name in right_map

        if in_left and in_right:
            lf = left_map[name]
            rf = right_map[name]
            if lf.type != rf.type:
                conflicts.append(
                    JoinConflict(
                        field_name=name,
                        left_type=lf.type.value,
                        right_type=rf.type.value,
                    )
                )
            chosen = lf if prefer == "left" else rf
            merged.append(chosen)
        elif in_left:
            left_only.append(name)
            merged.append(left_map[name])
        else:
            right_only.append(name)
            merged.append(right_map[name])

    result_schema = StreamSchema(name=left.name, fields=merged)
    return JoinResult(
        schema=result_schema,
        conflicts=conflicts,
        left_only=left_only,
        right_only=right_only,
    )
