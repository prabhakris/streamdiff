"""Partition schema fields into logical buckets based on a strategy."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class PartitionResult:
    strategy: str
    partitions: Dict[str, List[SchemaField]] = field(default_factory=dict)
    unpartitioned: List[SchemaField] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(self.partitions)

    def to_dict(self) -> dict:
        return {
            "strategy": self.strategy,
            "partitions": {
                k: [{"name": f.name, "type": f.field_type.value, "required": f.required} for f in v]
                for k, v in self.partitions.items()
            },
            "unpartitioned": [
                {"name": f.name, "type": f.field_type.value, "required": f.required}
                for f in self.unpartitioned
            ],
        }

    def __str__(self) -> str:
        lines = [f"Partition strategy: {self.strategy}"]
        for bucket, fields in self.partitions.items():
            lines.append(f"  [{bucket}]: {', '.join(f.name for f in fields)}")
        if self.unpartitioned:
            lines.append(f"  [unpartitioned]: {', '.join(f.name for f in self.unpartitioned)}")
        return "\n".join(lines)


def partition_by_required(schema: StreamSchema) -> PartitionResult:
    result = PartitionResult(strategy="required")
    result.partitions["required"] = [f for f in schema.fields if f.required]
    result.partitions["optional"] = [f for f in schema.fields if not f.required]
    return result


def partition_by_type(schema: StreamSchema) -> PartitionResult:
    result = PartitionResult(strategy="type")
    for f in schema.fields:
        bucket = f.field_type.value
        result.partitions.setdefault(bucket, []).append(f)
    return result


def partition_by_prefix(schema: StreamSchema, separator: str = "_") -> PartitionResult:
    result = PartitionResult(strategy="prefix")
    for f in schema.fields:
        if separator in f.name:
            prefix = f.name.split(separator)[0]
            result.partitions.setdefault(prefix, []).append(f)
        else:
            result.unpartitioned.append(f)
    return result


_STRATEGIES = {
    "required": partition_by_required,
    "type": partition_by_type,
    "prefix": partition_by_prefix,
}


def partition(schema: StreamSchema, strategy: str = "required", **kwargs) -> Optional[PartitionResult]:
    fn = _STRATEGIES.get(strategy)
    if fn is None:
        return None
    return fn(schema, **kwargs)
