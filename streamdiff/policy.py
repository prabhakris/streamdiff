"""Policy enforcement: define rules that must pass for a diff to be accepted."""
from dataclasses import dataclass, field
from typing import List, Optional
from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.severity import Severity, get_severity


@dataclass
class PolicyRule:
    name: str
    description: str
    max_severity: Severity = Severity.ERROR
    allow_breaking: bool = False
    blocked_change_types: List[ChangeType] = field(default_factory=list)


@dataclass
class PolicyViolation:
    rule: PolicyRule
    change: SchemaChange
    reason: str

    def __str__(self) -> str:
        return f"[{self.rule.name}] {self.reason} (field: {self.change.field_name})"


@dataclass
class PolicyResult:
    violations: List[PolicyViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def __bool__(self) -> bool:
        return self.passed


def _check_rule(rule: PolicyRule, change: SchemaChange) -> Optional[PolicyViolation]:
    if change.change_type in rule.blocked_change_types:
        return PolicyViolation(
            rule=rule,
            change=change,
            reason=f"change type '{change.change_type.value}' is blocked by policy",
        )
    severity = get_severity(change)
    if not rule.allow_breaking and severity == Severity.ERROR:
        return PolicyViolation(
            rule=rule,
            change=change,
            reason=f"breaking change detected (severity={severity.value})",
        )
    return None


def evaluate_policy(rule: PolicyRule, result: DiffResult) -> PolicyResult:
    violations = []
    for change in result.changes:
        violation = _check_rule(rule, change)
        if violation:
            violations.append(violation)
    return PolicyResult(violations=violations)
