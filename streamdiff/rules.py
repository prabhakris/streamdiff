"""Registry for named validation rules, allowing future extensibility."""
from typing import Callable, Dict, List, Optional

from streamdiff.diff import SchemaChange
from streamdiff.validator import ValidationIssue

RuleFunc = Callable[[SchemaChange], Optional[ValidationIssue]]

_registry: Dict[str, RuleFunc] = {}


def register(name: str) -> Callable[[RuleFunc], RuleFunc]:
    """Decorator to register a rule function by name."""
    def decorator(fn: RuleFunc) -> RuleFunc:
        _registry[name] = fn
        return fn
    return decorator


def get_rule(name: str) -> Optional[RuleFunc]:
    return _registry.get(name)


def list_rules() -> List[str]:
    return sorted(_registry.keys())


def apply_rules(
    change: SchemaChange,
    rule_names: Optional[List[str]] = None,
) -> List[ValidationIssue]:
    """Apply named rules (or all registered rules) to a single change."""
    names = rule_names if rule_names is not None else list_rules()
    issues: List[ValidationIssue] = []
    for name in names:
        fn = _registry.get(name)
        if fn is None:
            raise KeyError(f"Unknown rule: {name!r}")
        result = fn(change)
        if result is not None:
            issues.append(result)
    return issues
