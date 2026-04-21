"""Batch multiple DiffResults into a single aggregated report."""
from dataclasses import dataclass, field
from typing import List, Dict

from streamdiff.diff import DiffResult, SchemaChange, ChangeType


@dataclass
class BatchEntry:
    name: str
    result: DiffResult

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "changes": [
                {"field": c.field_name, "change": c.change_type.value, "breaking": c.breaking}
                for c in self.result.changes
            ],
            "has_breaking": any(c.breaking for c in self.result.changes),
        }

    def __str__(self) -> str:
        breaking = any(c.breaking for c in self.result.changes)
        flag = " [BREAKING]" if breaking else ""
        return f"{self.name}: {len(self.result.changes)} change(s){flag}"


@dataclass
class BatchReport:
    entries: List[BatchEntry] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(self.entries)

    def has_breaking(self) -> bool:
        return any(
            c.breaking
            for e in self.entries
            for c in e.result.changes
        )

    def total_changes(self) -> int:
        return sum(len(e.result.changes) for e in self.entries)

    def to_dict(self) -> dict:
        return {
            "total_entries": len(self.entries),
            "total_changes": self.total_changes(),
            "has_breaking": self.has_breaking(),
            "entries": [e.to_dict() for e in self.entries],
        }

    def by_name(self) -> Dict[str, BatchEntry]:
        return {e.name: e for e in self.entries}


def batch_results(named_results: List[tuple]) -> BatchReport:
    """Build a BatchReport from a list of (name, DiffResult) tuples."""
    entries = [BatchEntry(name=name, result=result) for name, result in named_results]
    return BatchReport(entries=entries)


def breaking_entries(report: BatchReport) -> List[BatchEntry]:
    """Return only entries that contain at least one breaking change."""
    return [
        e for e in report.entries
        if any(c.breaking for c in e.result.changes)
    ]
