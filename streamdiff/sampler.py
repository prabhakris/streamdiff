"""Sample a subset of fields from a schema by count or fraction."""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import List, Optional
from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class SampleResult:
    original_count: int
    sampled: List[SchemaField]
    seed: Optional[int]

    def __bool__(self) -> bool:
        return len(self.sampled) > 0

    def to_dict(self) -> dict:
        return {
            "original_count": self.original_count,
            "sampled_count": len(self.sampled),
            "seed": self.seed,
            "fields": [f.name for f in self.sampled],
        }

    def __str__(self) -> str:
        names = ", ".join(f.name for f in self.sampled)
        return f"SampleResult({len(self.sampled)}/{self.original_count}): {names}"

    def to_schema(self) -> StreamSchema:
        return StreamSchema(fields=list(self.sampled))


def sample_by_count(
    schema: StreamSchema,
    count: int,
    seed: Optional[int] = None,
) -> SampleResult:
    fields = list(schema.fields)
    count = max(0, min(count, len(fields)))
    rng = random.Random(seed)
    sampled = rng.sample(fields, count)
    return SampleResult(original_count=len(fields), sampled=sampled, seed=seed)


def sample_by_fraction(
    schema: StreamSchema,
    fraction: float,
    seed: Optional[int] = None,
) -> SampleResult:
    if not (0.0 <= fraction <= 1.0):
        raise ValueError(f"fraction must be between 0.0 and 1.0, got {fraction}")
    fields = list(schema.fields)
    count = round(len(fields) * fraction)
    rng = random.Random(seed)
    sampled = rng.sample(fields, count) if count > 0 else []
    return SampleResult(original_count=len(fields), sampled=sampled, seed=seed)
