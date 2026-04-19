"""Resolve field references across multiple schemas (e.g. shared/common fields)."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class ResolvedField:
    name: str
    source: str
    schema_field: SchemaField

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "source": self.source,
            "type": self.schema_field.field_type.value,
            "required": self.schema_field.required,
        }

    def __str__(self) -> str:
        req = "required" if self.schema_field.required else "optional"
        return f"{self.name} ({req}) from '{self.source}'"


@dataclass
class ResolveResult:
    resolved: List[ResolvedField] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.conflicts) == 0


def resolve_schemas(schemas: Dict[str, StreamSchema]) -> ResolveResult:
    """Merge field definitions from multiple named schemas, detecting conflicts."""
    seen: Dict[str, ResolvedField] = {}
    conflicts: List[str] = []
    result = ResolveResult()

    for source, schema in schemas.items():
        for name, f in schema.field_map().items():
            if name in seen:
                existing = seen[name]
                if existing.schema_field.field_type != f.field_type:
                    conflicts.append(
                        f"Field '{name}' type conflict: "
                        f"'{existing.source}' has {existing.schema_field.field_type.value}, "
                        f"'{source}' has {f.field_type.value}"
                    )
            else:
                rf = ResolvedField(name=name, source=source, schema_field=f)
                seen[name] = rf
                result.resolved.append(rf)

    result.conflicts = conflicts
    return result


def find_field(name: str, schemas: Dict[str, StreamSchema]) -> Optional[ResolvedField]:
    """Return the first schema that defines a given field name."""
    for source, schema in schemas.items():
        fm = schema.field_map()
        if name in fm:
            return ResolvedField(name=name, source=source, schema_field=fm[name])
    return None
