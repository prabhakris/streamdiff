"""Compose multiple StreamSchemas into a single unified schema."""
from dataclasses import dataclass, field
from typing import List, Optional

from streamdiff.schema import SchemaField, StreamSchema


@dataclass
class ComposeConflict:
    field_name: str
    sources: List[str]
    reason: str

    def __str__(self) -> str:
        srcs = ", ".join(self.sources)
        return f"conflict on '{self.field_name}' from [{srcs}]: {self.reason}"

    def to_dict(self) -> dict:
        return {
            "field": self.field_name,
            "sources": self.sources,
            "reason": self.reason,
        }


@dataclass
class ComposeResult:
    schema: Optional[StreamSchema]
    conflicts: List[ComposeConflict] = field(default_factory=list)
    source_names: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return len(self.conflicts) == 0

    def to_dict(self) -> dict:
        return {
            "ok": bool(self),
            "sources": self.source_names,
            "fields": [
                {"name": f.name, "type": f.field_type.value, "required": f.required}
                for f in (self.schema.fields if self.schema else [])
            ],
            "conflicts": [c.to_dict() for c in self.conflicts],
        }


def compose_schemas(
    named_schemas: List[tuple],  # list of (name, StreamSchema)
    on_conflict: str = "fail",  # "fail" | "first" | "last"
) -> ComposeResult:
    """Merge named schemas into one, detecting field-level conflicts."""
    seen: dict[str, tuple[str, SchemaField]] = {}
    conflicts: List[ComposeConflict] = []
    source_names = [n for n, _ in named_schemas]

    for source_name, schema in named_schemas:
        for f in schema.fields:
            if f.name not in seen:
                seen[f.name] = (source_name, f)
            else:
                prev_src, prev_field = seen[f.name]
                if prev_field.field_type != f.field_type:
                    conflicts.append(
                        ComposeConflict(
                            field_name=f.name,
                            sources=[prev_src, source_name],
                            reason=(
                                f"type mismatch: {prev_field.field_type.value}"
                                f" vs {f.field_type.value}"
                            ),
                        )
                    )
                    if on_conflict == "last":
                        seen[f.name] = (source_name, f)
                else:
                    # same type — keep required=True if either source requires it
                    merged = SchemaField(
                        name=f.name,
                        field_type=f.field_type,
                        required=prev_field.required or f.required,
                    )
                    seen[f.name] = (source_name, merged)

    if conflicts and on_conflict == "fail":
        return ComposeResult(schema=None, conflicts=conflicts, source_names=source_names)

    composed_fields = [sf for _, sf in seen.values()]
    composed = StreamSchema(name="composed", fields=composed_fields)
    return ComposeResult(schema=composed, conflicts=conflicts, source_names=source_names)
