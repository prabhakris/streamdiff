"""Slot fields into named buckets based on type or pattern."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from streamdiff.schema import StreamSchema, SchemaField, FieldType


@dataclass
class SlotResult:
    buckets: Dict[str, List[SchemaField]] = field(default_factory=dict)
    unslotted: List[SchemaField] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(self.buckets)

    def to_dict(self) -> dict:
        return {
            "buckets": {
                k: [{"name": f.name, "type": f.field_type.value} for f in v]
                for k, v in self.buckets.items()
            },
            "unslotted": [{"name": f.name, "type": f.field_type.value} for f in self.unslotted],
        }

    def __str__(self) -> str:
        lines = []
        for bucket, fields in self.buckets.items():
            lines.append(f"[{bucket}] {len(fields)} field(s)")
            for f in fields:
                lines.append(f"  - {f.name} ({f.field_type.value})")
        if self.unslotted:
            lines.append(f"[unslotted] {len(self.unslotted)} field(s)")
            for f in self.unslotted:
                lines.append(f"  - {f.name} ({f.field_type.value})")
        return "\n".join(lines) if lines else "No fields slotted."


def slot_by_type(schema: StreamSchema) -> SlotResult:
    """Group fields into buckets by their FieldType."""
    buckets: Dict[str, List[SchemaField]] = {}
    for f in schema.fields:
        key = f.field_type.value
        buckets.setdefault(key, []).append(f)
    return SlotResult(buckets=buckets, unslotted=[])


def slot_by_pattern(
    schema: StreamSchema,
    patterns: Dict[str, str],
) -> SlotResult:
    """Group fields into named buckets where field name contains pattern substring."""
    buckets: Dict[str, List[SchemaField]] = {k: [] for k in patterns}
    unslotted: List[SchemaField] = []
    for f in schema.fields:
        matched = False
        for bucket, pattern in patterns.items():
            if pattern.lower() in f.name.lower():
                buckets[bucket].append(f)
                matched = True
                break
        if not matched:
            unslotted.append(f)
    return SlotResult(buckets={k: v for k, v in buckets.items() if v}, unslotted=unslotted)
