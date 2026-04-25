"""Zip two schemas together by aligning fields by name."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from streamdiff.schema import SchemaField, StreamSchema


@dataclass
class ZipPair:
    name: str
    left: Optional[SchemaField]
    right: Optional[SchemaField]

    def aligned(self) -> bool:
        return self.left is not None and self.right is not None

    def only_left(self) -> bool:
        return self.left is not None and self.right is None

    def only_right(self) -> bool:
        return self.left is None and self.right is not None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "left": self.left.name if self.left else None,
            "left_type": self.left.field_type.value if self.left else None,
            "right": self.right.name if self.right else None,
            "right_type": self.right.field_type.value if self.right else None,
            "aligned": self.aligned(),
        }

    def __str__(self) -> str:
        l = f"{self.left.field_type.value}" if self.left else "(missing)"
        r = f"{self.right.field_type.value}" if self.right else "(missing)"
        return f"{self.name}: {l} | {r}"


@dataclass
class ZipResult:
    pairs: List[ZipPair] = field(default_factory=list)

    def __bool__(self) -> bool:
        return all(p.aligned() for p in self.pairs)

    def aligned(self) -> List[ZipPair]:
        return [p for p in self.pairs if p.aligned()]

    def unaligned(self) -> List[ZipPair]:
        return [p for p in self.pairs if not p.aligned()]

    def to_dict(self) -> dict:
        return {
            "total": len(self.pairs),
            "aligned": len(self.aligned()),
            "unaligned": len(self.unaligned()),
            "pairs": [p.to_dict() for p in self.pairs],
        }

    def __str__(self) -> str:
        lines = [str(p) for p in self.pairs]
        return "\n".join(lines) if lines else "(no fields)"


def zip_schemas(left: StreamSchema, right: StreamSchema) -> ZipResult:
    """Align fields from two schemas by name, producing a ZipResult."""
    left_map: Dict[str, SchemaField] = {f.name: f for f in left.fields}
    right_map: Dict[str, SchemaField] = {f.name: f for f in right.fields}
    all_names = sorted(set(left_map) | set(right_map))
    pairs = [
        ZipPair(
            name=name,
            left=left_map.get(name),
            right=right_map.get(name),
        )
        for name in all_names
    ]
    return ZipResult(pairs=pairs)
