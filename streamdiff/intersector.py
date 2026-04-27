"""intersector.py – compute the field intersection of two schemas."""
from dataclasses import dataclass, field
from typing import List

from streamdiff.schema import SchemaField, StreamSchema


@dataclass
class IntersectResult:
    """Result of intersecting two schemas."""
    common: List[SchemaField] = field(default_factory=list)
    only_left: List[SchemaField] = field(default_factory=list)
    only_right: List[SchemaField] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(self.common)

    def to_dict(self) -> dict:
        return {
            "common": [f.name for f in self.common],
            "only_left": [f.name for f in self.only_left],
            "only_right": [f.name for f in self.only_right],
            "common_count": len(self.common),
            "only_left_count": len(self.only_left),
            "only_right_count": len(self.only_right),
        }

    def __str__(self) -> str:
        lines = [f"common={len(self.common)}",
                 f"only_left={len(self.only_left)}",
                 f"only_right={len(self.only_right)}"]
        return "IntersectResult(" + ", ".join(lines) + ")"

    def to_schema(self) -> StreamSchema:
        """Return a StreamSchema containing only the common fields."""
        return StreamSchema(fields=list(self.common))


def intersect_schemas(left: StreamSchema, right: StreamSchema) -> IntersectResult:
    """Return fields present in both schemas, and those exclusive to each.

    A field is considered *common* when its name appears in both schemas.
    The field definition from *left* is used for common entries.
    Type compatibility is intentionally not checked here – use
    :mod:`streamdiff.comparator` for that.
    """
    left_map = left.field_map()
    right_map = right.field_map()

    common: List[SchemaField] = []
    only_left: List[SchemaField] = []
    only_right: List[SchemaField] = []

    for name, lf in left_map.items():
        if name in right_map:
            common.append(lf)
        else:
            only_left.append(lf)

    for name, rf in right_map.items():
        if name not in left_map:
            only_right.append(rf)

    return IntersectResult(common=common, only_left=only_left, only_right=only_right)
