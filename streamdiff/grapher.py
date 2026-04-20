"""Build a dependency graph of schema fields based on naming conventions and types."""
from dataclasses import dataclass, field
from typing import Dict, List, Set
from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class GraphNode:
    field: SchemaField
    neighbors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.field.name,
            "type": self.field.type.value,
            "required": self.field.required,
            "neighbors": self.neighbors,
        }

    def __str__(self) -> str:
        return f"{self.field.name} -> [{', '.join(self.neighbors)}]"


@dataclass
class FieldGraph:
    nodes: Dict[str, GraphNode] = field(default_factory=dict)

    def get(self, name: str) -> GraphNode | None:
        return self.nodes.get(name)

    def to_dict(self) -> dict:
        return {name: node.to_dict() for name, node in self.nodes.items()}


def _infer_edges(fields: List[SchemaField]) -> Dict[str, List[str]]:
    """Infer edges: fields sharing a common prefix are considered related."""
    edges: Dict[str, List[str]] = {f.name: [] for f in fields}
    names = [f.name for f in fields]
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            prefix_a = a.split("_")[0]
            prefix_b = b.split("_")[0]
            if prefix_a == prefix_b and prefix_a:
                edges[a].append(b)
                edges[b].append(a)
    return edges


def build_graph(schema: StreamSchema) -> FieldGraph:
    fields = list(schema.field_map.values())
    edges = _infer_edges(fields)
    nodes = {
        f.name: GraphNode(field=f, neighbors=sorted(set(edges.get(f.name, []))))
        for f in fields
    }
    return FieldGraph(nodes=nodes)


def isolated_fields(graph: FieldGraph) -> List[str]:
    """Return names of fields with no inferred neighbors."""
    return [name for name, node in graph.nodes.items() if not node.neighbors]
