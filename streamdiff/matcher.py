"""Field matcher: find best-match fields between two schemas by name and type."""
from dataclasses import dataclass
from typing import List, Optional
from streamdiff.schema import SchemaField, StreamSchema


@dataclass
class FieldMatch:
    old_field: SchemaField
    new_field: SchemaField
    name_match: bool
    type_match: bool

    @property
    def exact(self) -> bool:
        return self.name_match and self.type_match

    def to_dict(self) -> dict:
        return {
            "old": self.old_field.name,
            "new": self.new_field.name,
            "name_match": self.name_match,
            "type_match": self.type_match,
            "exact": self.exact,
        }

    def __str__(self) -> str:
        status = "exact" if self.exact else "partial"
        return f"{self.old_field.name} -> {self.new_field.name} ({status})"


@dataclass
class MatchReport:
    matches: List[FieldMatch]
    unmatched_old: List[SchemaField]
    unmatched_new: List[SchemaField]

    def __bool__(self) -> bool:
        return len(self.unmatched_old) == 0 and len(self.unmatched_new) == 0

    def to_dict(self) -> dict:
        return {
            "matches": [m.to_dict() for m in self.matches],
            "unmatched_old": [f.name for f in self.unmatched_old],
            "unmatched_new": [f.name for f in self.unmatched_new],
        }


def _find_match(field: SchemaField, candidates: List[SchemaField]) -> Optional[SchemaField]:
    for c in candidates:
        if c.name == field.name:
            return c
    return None


def match_schemas(old: StreamSchema, new: StreamSchema) -> MatchReport:
    matches: List[FieldMatch] = []
    unmatched_old: List[SchemaField] = []
    matched_new_names = set()

    for old_field in old.fields:
        new_field = _find_match(old_field, new.fields)
        if new_field is not None:
            matches.append(FieldMatch(
                old_field=old_field,
                new_field=new_field,
                name_match=True,
                type_match=(old_field.type == new_field.type),
            ))
            matched_new_names.add(new_field.name)
        else:
            unmatched_old.append(old_field)

    unmatched_new = [f for f in new.fields if f.name not in matched_new_names]
    return MatchReport(matches=matches, unmatched_old=unmatched_old, unmatched_new=unmatched_new)
