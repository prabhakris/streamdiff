"""Tests for streamdiff.rules registry."""
import pytest

from streamdiff.schema import SchemaField, FieldType
from streamdiff.diff import SchemaChange, ChangeType
from streamdiff.rules import register, get_rule, list_rules, apply_rules
from streamdiff.validator import ValidationIssue


def _field(name: str) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=False)


def _removed_change(name: str = "f") -> SchemaChange:
    return SchemaChange(
        field_name=name,
        change_type=ChangeType.REMOVED,
        old_field=_field(name),
        new_field=None,
    )


def test_register_and_get_rule():
    @register("TEST_RULE")
    def my_rule(change):
        return None

    assert get_rule("TEST_RULE") is my_rule


def test_list_rules_includes_registered():
    @register("ALPHA_RULE")
    def alpha(change):
        return None

    assert "ALPHA_RULE" in list_rules()


def test_apply_rules_no_issue():
    @register("ALWAYS_PASS")
    def always_pass(change):
        return None

    issues = apply_rules(_removed_change(), rule_names=["ALWAYS_PASS"])
    assert issues == []


def test_apply_rules_with_issue():
    @register("ALWAYS_FAIL")
    def always_fail(change):
        return ValidationIssue(change=change, rule="ALWAYS_FAIL", message="forced failure")

    issues = apply_rules(_removed_change(), rule_names=["ALWAYS_FAIL"])
    assert len(issues) == 1
    assert issues[0].rule == "ALWAYS_FAIL"


def test_apply_rules_unknown_raises():
    with pytest.raises(KeyError, match="NONEXISTENT"):
        apply_rules(_removed_change(), rule_names=["NONEXISTENT"])


def test_apply_all_rules_when_none_specified():
    @register("BETA_RULE")
    def beta(change):
        return None

    # Should not raise; runs all registered rules
    issues = apply_rules(_removed_change())
    assert isinstance(issues, list)
