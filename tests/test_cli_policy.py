import argparse
import pytest
from streamdiff.diff import SchemaChange, ChangeType, DiffResult
from streamdiff.schema import SchemaField, FieldType
from streamdiff.policy import PolicyRule, PolicyViolation, PolicyResult
from streamdiff.cli_policy import (
    add_policy_args,
    build_policy_rule,
    handle_policy_output,
    _parse_blocked_types,
)


def _parse(args):
    p = argparse.ArgumentParser()
    add_policy_args(p)
    return p.parse_args(args)


def _field(name="f", required=True):
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change():
    return SchemaChange(field_name="f", change_type=ChangeType.REMOVED, before=_field(), after=None)


def test_add_policy_args_defaults():
    ns = _parse([])
    assert ns.policy_name == "default"
    assert ns.allow_breaking is False
    assert ns.block_types == []
    assert ns.policy_json is False


def test_add_policy_args_custom():
    ns = _parse(["--policy-name", "strict", "--allow-breaking", "--block-types", "removed"])
    assert ns.policy_name == "strict"
    assert ns.allow_breaking is True
    assert "removed" in ns.block_types


def test_build_policy_rule_defaults():
    ns = _parse([])
    rule = build_policy_rule(ns)
    assert rule.name == "default"
    assert rule.allow_breaking is False
    assert rule.blocked_change_types == []


def test_build_policy_rule_blocked_types():
    ns = _parse(["--block-types", "removed", "type_changed"])
    rule = build_policy_rule(ns)
    assert ChangeType.REMOVED in rule.blocked_change_types
    assert ChangeType.TYPE_CHANGED in rule.blocked_change_types


def test_parse_blocked_types_ignores_invalid():
    result = _parse_blocked_types(["removed", "not_a_type"])
    assert ChangeType.REMOVED in result
    assert len(result) == 1


def test_handle_policy_output_passed_returns_zero(capsys):
    pr = PolicyResult(violations=[])
    code = handle_policy_output(pr, use_json=False)
    assert code == 0
    out = capsys.readouterr().out
    assert "passed" in out.lower()


def test_handle_policy_output_failed_returns_one(capsys):
    rule = PolicyRule(name="r", description="d")
    v = PolicyViolation(rule=rule, change=_change(), reason="breaking")
    pr = PolicyResult(violations=[v])
    code = handle_policy_output(pr, use_json=False)
    assert code == 1


def test_handle_policy_output_json(capsys):
    import json
    pr = PolicyResult(violations=[])
    handle_policy_output(pr, use_json=True)
    data = json.loads(capsys.readouterr().out)
    assert data["passed"] is True
    assert data["violations"] == []
