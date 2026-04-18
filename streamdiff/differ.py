"""High-level differ that wires together diff, filter, severity, and scoring."""
from dataclasses import dataclass
from typing import Optional

from streamdiff.diff import DiffResult, compute_diff
from streamdiff.filter import filter_changes
from streamdiff.severity import annotate_changes, filter_by_severity, Severity
from streamdiff.scorer import score_result, RiskScore
from streamdiff.schema import StreamSchema


@dataclass
class DifferConfig:
    min_severity: Optional[Severity] = None
    include_fields: Optional[list] = None
    exclude_fields: Optional[list] = None
    score: bool = False


@dataclass
class DifferResult:
    diff: DiffResult
    risk_score: Optional[RiskScore] = None

    @property
    def has_breaking(self) -> bool:
        from streamdiff.diff import has_breaking_changes
        return has_breaking_changes(self.diff)


def run_diff(old: StreamSchema, new: StreamSchema, config: Optional[DifferConfig] = None) -> DifferResult:
    if config is None:
        config = DifferConfig()

    result = compute_diff(old, new)

    changes = filter_changes(
        result.changes,
        include=config.include_fields,
        exclude=config.exclude_fields,
    )

    changes = annotate_changes(changes)

    if config.min_severity is not None:
        changes = filter_by_severity(changes, config.min_severity)

    result = DiffResult(changes=changes)

    risk = score_result(result) if config.score else None
    return DifferResult(diff=result, risk_score=risk)
