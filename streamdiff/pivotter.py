"""Pivot a schema by grouping fields into a table-like structure keyed by a dimension."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class PivotCell:
    field_name: str
    field_type: str
    required: bool

    def to_dict(self) -> dict:
        return {
            "field_name": self.field_name,
            "field_type": self.field_type,
            "required": self.required,
        }

    def __str__(self) -> str:
        req = "required" if self.required else "optional"
        return f"{self.field_name} ({self.field_type}, {req})"


@dataclass
class PivotRow:
    dimension: str
    cells: List[PivotCell] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "cells": [c.to_dict() for c in self.cells],
        }


@dataclass
class PivotResult:
    rows: List[PivotRow] = field(default_factory=list)
    dimension_key: str = "prefix"

    def __bool__(self) -> bool:
        return len(self.rows) > 0

    def to_dict(self) -> dict:
        return {
            "dimension_key": self.dimension_key,
            "rows": [r.to_dict() for r in self.rows],
        }

    def __str__(self) -> str:
        if not self.rows:
            return "PivotResult: empty"
        lines = [f"Pivot by {self.dimension_key}:"]
        for row in self.rows:
            lines.append(f"  [{row.dimension}]")
            for cell in row.cells:
                lines.append(f"    - {cell}")
        return "\n".join(lines)


def _extract_dimension(name: str, separator: str = ".") -> str:
    parts = name.split(separator, 1)
    return parts[0] if len(parts) > 1 else "__root__"


def pivot_schema(
    schema: StreamSchema,
    separator: str = ".",
    dimension_key: str = "prefix",
) -> PivotResult:
    groups: Dict[str, List[SchemaField]] = {}
    for f in schema.fields:
        dim = _extract_dimension(f.name, separator)
        groups.setdefault(dim, []).append(f)

    rows = []
    for dim in sorted(groups):
        cells = [
            PivotCell(
                field_name=f.name,
                field_type=f.field_type.value,
                required=f.required,
            )
            for f in groups[dim]
        ]
        rows.append(PivotRow(dimension=dim, cells=cells))

    return PivotResult(rows=rows, dimension_key=dimension_key)
