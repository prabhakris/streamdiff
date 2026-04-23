"""capper.py — cap (limit) the number of changes reported per change type."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from streamdiff.diff import DiffResult, SchemaChange, ChangeType


@dataclass
class CapResult:
    kept: List[SchemaChange] = field(default_factory=list)
    dropped: List[SchemaChange] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(self.kept)

    def to_dict(self) -> dict:
        return {
            "kept": [c.field_name for c in self.kept],
            "dropped": [c.field_name for c in self.dropped],
            "kept_count": len(self.kept),
            "dropped_count": len(self.dropped),
        }

    def __str__(self) -> str:
        return (
            f"CapResult(kept={len(self.kept)}, dropped={len(self.dropped)})"
        )


def cap_by_type(
    changes: List[SchemaChange],
    limits: Dict[ChangeType, int],
    default_limit: int = 0,
) -> CapResult:
    """Keep at most *limit* changes per ChangeType.

    Args:
        changes: flat list of SchemaChange objects.
        limits: mapping from ChangeType to maximum allowed count.
        default_limit: limit applied to any type not present in *limits*.
            0 means no cap (unlimited).

    Returns:
        CapResult with *kept* and *dropped* lists.
    """
    counters: Dict[ChangeType, int] = {}
    kept: List[SchemaChange] = []
    dropped: List[SchemaChange] = []

    for change in changes:
        limit = limits.get(change.change_type, default_limit)
        current = counters.get(change.change_type, 0)
        if limit == 0 or current < limit:
            kept.append(change)
            counters[change.change_type] = current + 1
        else:
            dropped.append(change)

    return CapResult(kept=kept, dropped=dropped)


def cap_result(
    result: DiffResult,
    limits: Dict[ChangeType, int],
    default_limit: int = 0,
) -> CapResult:
    """Convenience wrapper that accepts a full DiffResult."""
    return cap_by_type(
        result.changes, limits=limits, default_limit=default_limit
    )
