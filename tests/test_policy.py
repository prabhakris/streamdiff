import pytest
from streamdiff.diff import SchemaChange, ChangeType, DiffResult
from streamdiff.schema import SchemaField, FieldType
from streamdiff.policy import (
    PolicyRule,
    PolicyViolation,
    PolicyResult,
    evaluate_policy,
)


def _field(name="f", required=True):
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(change_type=ChangeType.REMOVED, name="f", required=True):
    return SchemaChange(field_name=name, change_type=change_type, before=_field(name, required), after=None)


def _result(*changes):
    return DiffResult(changes=list(changes))


def _rule(**kwargs):
    defaults = dict(name="test", description="test rule")
    defaults.update(kwargs)
    return PolicyRule(**defaults)


def test_no_changes_passes():
    rule = _rule()
    result = evaluate_policy(rule, _result())
    assert result.passed


def test_added_optional_passes():
    change = SchemaChange(
        field_name="x",
        change_type=ChangeType.ADDED,
        before=None,
        after=_field("x", required=False),
    )
    rule = _rule()
    result = evaluate_policy(rule, _result(change))
    assert result.passed


def test_removed_field_violates_no_breaking_rule():
    rule = _rule(allow_breaking=False)
    result = evaluate_policy(rule, _result(_change(ChangeType.REMOVED)))
    assert not result.passed
    assert len(result.violations) == 1
    assert "breaking" in result.violations[0].reason


def test_allow_breaking_skips_severity_check():
    rule = _rule(allow_breaking=True)
    result = evaluate_policy(rule, _result(_change(ChangeType.REMOVED)))
    assert result.passed


def test_blocked_change_type_triggers_violation():
    rule = _rule(allow_breaking=True, blocked_change_types=[ChangeType.TYPE_CHANGED])
    change = SchemaChange(
        field_name="f",
        change_type=ChangeType.TYPE_CHANGED,
        before=_field(),
        after=_field(),
    )
    result = evaluate_policy(rule, _result(change))
    assert not result.passed
    assert "blocked" in result.violations[0].reason


def test_policy_result_bool_true_when_no_violations():
    pr = PolicyResult(violations=[])
    assert bool(pr) is True


def test_policy_result_bool_false_when_violations():
    rule = _rule()
    v = PolicyViolation(rule=rule, change=_change(), reason="bad")
    pr = PolicyResult(violations=[v])
    assert bool(pr) is False


def test_violation_str_contains_rule_name_and_field():
    rule = _rule(name="strict")
    v = PolicyViolation(rule=rule, change=_change(name="user_id"), reason="blocked")
    s = str(v)
    assert "strict" in s
    assert "user_id" in s
