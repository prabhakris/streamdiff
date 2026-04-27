"""linker.py — link fields across two schemas by name and type similarity."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from streamdiff.schema import SchemaField, StreamSchema


@dataclass
class FieldLink:
    left: SchemaField
    right: SchemaField
    exact: bool  # True when name AND type both match

    def to_dict(self) -> dict:
        return {
            "left": self.left.name,
            "right": self.right.name,
            "left_type": self.left.field_type.value,
            "right_type": self.right.field_type.value,
            "exact": self.exact,
        }

    def __str__(self) -> str:
        tag = "exact" if self.exact else "fuzzy"
        return (
            f"{self.left.name} ({self.left.field_type.value})"
            f" <-[{tag}]-> "
            f"{self.right.name} ({self.right.field_type.value})"
        )


@dataclass
class LinkReport:
    links: List[FieldLink] = field(default_factory=list)
    unlinked_left: List[SchemaField] = field(default_factory=list)
    unlinked_right: List[SchemaField] = field(default_factory=list)

    def __bool__(self) -> bool:
        return len(self.links) > 0

    def to_dict(self) -> dict:
        return {
            "links": [lk.to_dict() for lk in self.links],
            "unlinked_left": [f.name for f in self.unlinked_left],
            "unlinked_right": [f.name for f in self.unlinked_right],
        }


def _find_right(name: str, right_map: dict) -> Optional[SchemaField]:
    """Return the right-side field whose name matches, or None."""
    return right_map.get(name)


def link_schemas(left: StreamSchema, right: StreamSchema) -> LinkReport:
    """Link fields between *left* and *right* by name; mark exact when types also agree."""
    left_map = left.field_map()
    right_map = right.field_map()

    links: List[FieldLink] = []
    linked_right: set = set()

    for name, lf in left_map.items():
        rf = _find_right(name, right_map)
        if rf is not None:
            exact = lf.field_type == rf.field_type
            links.append(FieldLink(left=lf, right=rf, exact=exact))
            linked_right.add(name)

    unlinked_left = [f for n, f in left_map.items() if n not in {lk.left.name for lk in links}]
    unlinked_right = [f for n, f in right_map.items() if n not in linked_right]

    return LinkReport(links=links, unlinked_left=unlinked_left, unlinked_right=unlinked_right)
