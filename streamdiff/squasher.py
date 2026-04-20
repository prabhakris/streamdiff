"""Squash multiple DiffResults into a single consolidated result."""
from dataclasses import dataclass, field
from typing import List

from streamdiff.diff import DiffResult, SchemaChange, ChangeType


@dataclass
class SquashResult:
    changes: List[SchemaChange] = field(default_factory=list)
    source_count: int = 0

    def __bool__(self) -> bool:
        return len(self.changes) > 0

    def to_dict(self) -> dict:
        return {
            "source_count": self.source_count,
            "change_count": len(self.changes),
            "changes": [
                {
                    "field": c.field_name,
                    "change_type": c.change_type.value,
                    "breaking": c.breaking,
                }
                for c in self.changes
            ],
        }

    def __str__(self) -> str:
        if not self.changes:
            return f"Squashed {self.source_count} result(s): no changes."
        lines = [f"Squashed {self.source_count} result(s): {len(self.changes)} unique change(s)."]
        for c in self.changes:
            marker = " [BREAKING]" if c.breaking else ""
            lines.append(f"  {c.change_type.value}: {c.field_name}{marker}")
        return "\n".join(lines)


def _change_key(change: SchemaChange) -> tuple:
    return (change.field_name, change.change_type)


def squash(results: List[DiffResult]) -> SquashResult:
    """Merge multiple DiffResults, deduplicating by (field_name, change_type)."""
    seen: dict = {}
    for result in results:
        for change in result.changes:
            key = _change_key(change)
            if key not in seen:
                seen[key] = change
            else:
                # prefer breaking=True if either source marks it breaking
                if change.breaking and not seen[key].breaking:
                    seen[key] = change
    return SquashResult(
        changes=list(seen.values()),
        source_count=len(results),
    )
