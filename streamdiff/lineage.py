"""Field lineage tracking across multiple schema versions."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class LineageNode:
    """A single field state at a specific version."""
    version: str
    field: Optional[SchemaField]  # None means field absent at this version

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "present": self.field is not None,
            "type": self.field.field_type.value if self.field else None,
            "required": self.field.required if self.field else None,
        }


@dataclass
class FieldLineage:
    """Lineage of a single field across versions."""
    name: str
    nodes: List[LineageNode] = field(default_factory=list)

    def first_seen(self) -> Optional[str]:
        """Return the version where this field first appeared."""
        for node in self.nodes:
            if node.field is not None:
                return node.version
        return None

    def last_seen(self) -> Optional[str]:
        """Return the version where this field was last present."""
        result = None
        for node in self.nodes:
            if node.field is not None:
                result = node.version
        return result

    def is_stable(self) -> bool:
        """Return True if the field is present in every version."""
        return all(n.field is not None for n in self.nodes)

    def type_changes(self) -> List[Dict]:
        """Return list of version pairs where the field type changed."""
        changes = []
        prev = None
        for node in self.nodes:
            if node.field is not None and prev is not None:
                if prev.field_type != node.field.field_type:
                    changes.append({
                        "version": node.version,
                        "from": prev.field_type.value,
                        "to": node.field.field_type.value,
                    })
            if node.field is not None:
                prev = node.field
        return changes

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "first_seen": self.first_seen(),
            "last_seen": self.last_seen(),
            "stable": self.is_stable(),
            "type_changes": self.type_changes(),
            "nodes": [n.to_dict() for n in self.nodes],
        }


@dataclass
class LineageReport:
    """Lineage report for all fields across a sequence of schema versions."""
    versions: List[str]
    lineages: List[FieldLineage] = field(default_factory=list)

    def get(self, name: str) -> Optional[FieldLineage]:
        for lin in self.lineages:
            if lin.name == name:
                return lin
        return None

    def unstable_fields(self) -> List[FieldLineage]:
        """Return fields that are not present in every version."""
        return [lin for lin in self.lineages if not lin.is_stable()]

    def to_dict(self) -> dict:
        return {
            "versions": self.versions,
            "fields": [lin.to_dict() for lin in self.lineages],
        }


def build_lineage(versioned: List[tuple]) -> LineageReport:
    """Build a LineageReport from a list of (version_label, StreamSchema) tuples."""
    versions = [v for v, _ in versioned]
    all_names: Dict[str, FieldLineage] = {}

    for version, schema in versioned:
        field_map = schema.field_map()
        # Ensure every previously seen field gets a node for this version
        for name, lin in all_names.items():
            lin.nodes.append(LineageNode(version=version, field=field_map.get(name)))
        # Add newly discovered fields
        for name, f in field_map.items():
            if name not in all_names:
                # Back-fill absent nodes for prior versions
                prior_nodes = [
                    LineageNode(version=v, field=None)
                    for v, _ in versioned
                    if v != version and v in versions[:versions.index(version)]
                ]
                lin = FieldLineage(name=name, nodes=prior_nodes)
                lin.nodes.append(LineageNode(version=version, field=f))
                all_names[name] = lin

    return LineageReport(versions=versions, lineages=list(all_names.values()))
