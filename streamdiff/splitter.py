"""Split a StreamSchema into sub-schemas based on field name prefixes or tags."""
from dataclasses import dataclass, field
from typing import Dict, List
from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class SplitResult:
    groups: Dict[str, StreamSchema]
    unmatched: StreamSchema

    def __bool__(self) -> bool:
        return bool(self.groups)

    def to_dict(self) -> dict:
        return {
            "groups": {k: [f.name for f in v.fields] for k, v in self.groups.items()},
            "unmatched": [f.name for f in self.unmatched.fields],
        }


def _make_schema(name: str, fields: List[SchemaField]) -> StreamSchema:
    s = StreamSchema(name=name, fields=fields)
    return s


def split_by_prefix(schema: StreamSchema, separator: str = "_") -> SplitResult:
    """Group fields by the first component of their name when split by separator."""
    buckets: Dict[str, List[SchemaField]] = {}
    unmatched: List[SchemaField] = []

    for f in schema.fields:
        if separator in f.name:
            prefix = f.name.split(separator, 1)[0]
            buckets.setdefault(prefix, []).append(f)
        else:
            unmatched.append(f)

    groups = {k: _make_schema(f"{schema.name}.{k}", v) for k, v in buckets.items()}
    return SplitResult(groups=groups, unmatched=_make_schema(f"{schema.name}.unmatched", unmatched))


def split_by_names(schema: StreamSchema, name_sets: Dict[str, List[str]]) -> SplitResult:
    """Partition fields into named groups by explicit field-name lists."""
    assigned: Dict[str, List[SchemaField]] = {k: [] for k in name_sets}
    unmatched: List[SchemaField] = []
    lookup: Dict[str, str] = {n: grp for grp, names in name_sets.items() for n in names}

    for f in schema.fields:
        grp = lookup.get(f.name)
        if grp:
            assigned[grp].append(f)
        else:
            unmatched.append(f)

    groups = {k: _make_schema(f"{schema.name}.{k}", v) for k, v in assigned.items()}
    return SplitResult(groups=groups, unmatched=_make_schema(f"{schema.name}.unmatched", unmatched))
