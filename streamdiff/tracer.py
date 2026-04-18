"""Field lineage tracer: tracks how fields evolve across multiple schema versions."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class TraceEntry:
    version: str
    present: bool
    field_type: Optional[str] = None
    required: Optional[bool] = None

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "present": self.present,
            "field_type": self.field_type,
            "required": self.required,
        }


@dataclass
class FieldTrace:
    field_name: str
    entries: List[TraceEntry] = field(default_factory=list)

    def added_in(self) -> Optional[str]:
        for e in self.entries:
            if e.present:
                return e.version
        return None

    def removed_in(self) -> Optional[str]:
        found = False
        for e in self.entries:
            if e.present:
                found = True
            elif found:
                return e.version
        return None

    def to_dict(self) -> dict:
        return {
            "field": self.field_name,
            "added_in": self.added_in(),
            "removed_in": self.removed_in(),
            "history": [e.to_dict() for e in self.entries],
        }


def trace_field(
    field_name: str,
    versions: List[tuple],  # list of (version_label, StreamSchema)
) -> FieldTrace:
    entries = []
    for label, schema in versions:
        fm = schema.field_map()
        if field_name in fm:
            f = fm[field_name]
            entries.append(TraceEntry(label, True, f.field_type.value, f.required))
        else:
            entries.append(TraceEntry(label, False))
    return FieldTrace(field_name, entries)


def trace_all(versions: List[tuple]) -> Dict[str, FieldTrace]:
    all_names: set = set()
    for _, schema in versions:
        all_names.update(schema.field_map().keys())
    return {name: trace_field(name, versions) for name in sorted(all_names)}
