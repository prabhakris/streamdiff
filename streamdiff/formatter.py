"""Formatters for schema change summaries."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from streamdiff.diff import DiffResult, ChangeType


@dataclass
class SummaryLine:
    symbol: str
    label: str
    count: int

    def __str__(self) -> str:
        return f"{self.symbol} {self.label}: {self.count}"


def build_summary(result: DiffResult) -> List[SummaryLine]:
    """Return a list of SummaryLine objects describing the diff result."""
    added = sum(1 for c in result.changes if c.change_type == ChangeType.ADDED)
    removed = sum(1 for c in result.changes if c.change_type == ChangeType.REMOVED)
    modified = sum(1 for c in result.changes if c.change_type == ChangeType.TYPE_CHANGED)
    breaking = sum(1 for c in result.changes if c.breaking)

    return [
        SummaryLine("+", "added", added),
        SummaryLine("-", "removed", removed),
        SummaryLine("~", "modified", modified),
        SummaryLine("!", "breaking", breaking),
    ]


def format_summary_text(result: DiffResult) -> str:
    """Return a plain-text summary string for the diff result."""
    lines = build_summary(result)
    total = len(result.changes)
    header = f"Schema diff summary ({total} change(s)):"
    body = "  ".join(str(l) for l in lines)
    return f"{header}\n  {body}"


def format_summary_dict(result: DiffResult) -> dict:
    """Return a dict representation of the summary suitable for JSON output."""
    lines = build_summary(result)
    return {
        "total_changes": len(result.changes),
        "has_breaking": result.has_breaking,
        "counts": {l.label: l.count for l in lines},
    }
