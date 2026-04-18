"""Normalize schema field names before comparison (e.g. snake_case vs camelCase)."""

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List

from streamdiff.schema import StreamSchema, SchemaField


def _snake_to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


def _camel_to_snake(name: str) -> str:
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


def _lowercase(name: str) -> str:
    return name.lower()


STRATEGIES: Dict[str, Callable[[str], str]] = {
    "snake_to_camel": _snake_to_camel,
    "camel_to_snake": _camel_to_snake,
    "lowercase": _lowercase,
    "none": lambda n: n,
}


@dataclass
class NormalizeConfig:
    strategy: str = "none"

    def get_fn(self) -> Callable[[str], str]:
        if self.strategy not in STRATEGIES:
            raise ValueError(
                f"Unknown normalization strategy '{self.strategy}'. "
                f"Choose from: {list(STRATEGIES)}"
            )
        return STRATEGIES[self.strategy]


def normalize_field(f: SchemaField, fn: Callable[[str], str]) -> SchemaField:
    return SchemaField(
        name=fn(f.name),
        field_type=f.field_type,
        required=f.required,
        nullable=f.nullable,
    )


def normalize_schema(schema: StreamSchema, config: NormalizeConfig) -> StreamSchema:
    fn = config.get_fn()
    normalized: List[SchemaField] = [normalize_field(f, fn) for f in schema.fields]
    return StreamSchema(name=schema.name, fields=normalized)
