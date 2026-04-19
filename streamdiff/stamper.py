"""Stamper: attach version stamps to schemas and compare stamp metadata."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from streamdiff.schema import StreamSchema


@dataclass
class SchemaStamp:
    version: str
    author: str
    timestamp: str
    description: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "author": self.author,
            "timestamp": self.timestamp,
            "description": self.description,
            "tags": self.tags,
        }

    def __str__(self) -> str:
        tag_str = ", ".join(self.tags) if self.tags else "none"
        return (
            f"v{self.version} by {self.author} at {self.timestamp} "
            f"[{tag_str}]: {self.description}"
        )


@dataclass
class StampedSchema:
    schema: StreamSchema
    stamp: SchemaStamp

    def to_dict(self) -> dict:
        return {
            "stamp": self.stamp.to_dict(),
            "fields": [
                {"name": f.name, "type": f.type.value, "required": f.required}
                for f in self.schema.fields
            ],
        }


def stamp_schema(
    schema: StreamSchema,
    version: str,
    author: str,
    description: str = "",
    tags: Optional[list[str]] = None,
    ts: Optional[str] = None,
) -> StampedSchema:
    timestamp = ts or datetime.now(timezone.utc).isoformat()
    stamp = SchemaStamp(
        version=version,
        author=author,
        timestamp=timestamp,
        description=description,
        tags=tags or [],
    )
    return StampedSchema(schema=schema, stamp=stamp)


def compare_stamps(a: SchemaStamp, b: SchemaStamp) -> dict:
    """Return a dict describing differences between two stamps."""
    diffs: dict = {}
    if a.version != b.version:
        diffs["version"] = {"old": a.version, "new": b.version}
    if a.author != b.author:
        diffs["author"] = {"old": a.author, "new": b.author}
    added_tags = sorted(set(b.tags) - set(a.tags))
    removed_tags = sorted(set(a.tags) - set(b.tags))
    if added_tags or removed_tags:
        diffs["tags"] = {"added": added_tags, "removed": removed_tags}
    return diffs
