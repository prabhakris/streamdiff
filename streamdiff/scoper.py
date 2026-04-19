"""Scope filtering: restrict diff to a subset of fields by path prefix or pattern."""
from __future__ import annotations
from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import List, Optional

from streamdiff.diff import DiffResult, SchemaChange


@dataclass
class ScopeConfig:
    includes: List[str] = field(default_factory=list)  # glob patterns
    excludes: List[str] = field(default_factory=list)  # glob patterns

    def __bool__(self) -> bool:
        return bool(self.includes or self.excludes)


@dataclass
class ScopeResult:
    changes: List[SchemaChange]
    total_before: int
    total_after: int

    @property
    def dropped(self) -> int:
        return self.total_before - self.total_after

    def to_dict(self) -> dict:
        return {
            "changes": [{"field": c.field_name, "change_type": c.change_type.value} for c in self.changes],
            "total_before": self.total_before,
            "total_after": self.total_after,
            "dropped": self.dropped,
        }


def _matches_any(name: str, patterns: List[str]) -> bool:
    return any(fnmatch(name, p) for p in patterns)


def apply_scope(result: DiffResult, config: ScopeConfig) -> ScopeResult:
    """Filter DiffResult changes according to include/exclude glob patterns."""
    changes = list(result.changes)
    total_before = len(changes)

    if config.includes:
        changes = [c for c in changes if _matches_any(c.field_name, config.includes)]

    if config.excludes:
        changes = [c for c in changes if not _matches_any(c.field_name, config.excludes)]

    return ScopeResult(
        changes=changes,
        total_before=total_before,
        total_after=len(changes),
    )


def scope_field_names(names: List[str], config: ScopeConfig) -> List[str]:
    """Apply scope config to a plain list of field names."""
    result = list(names)
    if config.includes:
        result = [n for n in result if _matches_any(n, config.includes)]
    if config.excludes:
        result = [n for n in result if not _matches_any(n, config.excludes)]
    return result
