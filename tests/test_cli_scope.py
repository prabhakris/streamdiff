import argparse
import pytest
from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType
from streamdiff.cli_scope import add_scope_args, build_scope_config, apply_scope_args, format_scope_summary


def _field(name: str) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=False)


def _change(name: str) -> SchemaChange:
    return SchemaChange(field_name=name, change_type=ChangeType.ADDED, old_field=None, new_field=_field(name))


def _result(*names: str) -> DiffResult:
    return DiffResult(changes=[_change(n) for n in names])


def _parse(args: list) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    add_scope_args(p)
    return p.parse_args(args)


def test_add_scope_args_defaults():
    ns = _parse([])
    assert ns.scope_include == []
    assert ns.scope_exclude == []


def test_add_scope_args_include():
    ns = _parse(["--scope-include", "user.*"])
    assert ns.scope_include == ["user.*"]


def test_add_scope_args_exclude():
    ns = _parse(["--scope-exclude", "internal.*"])
    assert ns.scope_exclude == ["internal.*"]


def test_build_scope_config_empty():
    ns = _parse([])
    cfg = build_scope_config(ns)
    assert not cfg


def test_build_scope_config_with_patterns():
    ns = _parse(["--scope-include", "a.*", "--scope-exclude", "b.*"])
    cfg = build_scope_config(ns)
    assert cfg.includes == ["a.*"]
    assert cfg.excludes == ["b.*"]


def test_apply_scope_args_filters():
    ns = _parse(["--scope-include", "user.*"])
    r = _result("user.id", "user.name", "order.total")
    out = apply_scope_args(r, ns)
    assert out.total_after == 2
    assert out.dropped == 1


def test_format_scope_summary_contains_counts():
    ns = _parse(["--scope-include", "x"])
    r = _result("x", "y")
    out = apply_scope_args(r, ns)
    summary = format_scope_summary(out)
    assert "1 shown" in summary
    assert "1 dropped" in summary


def test_format_scope_summary_lists_fields():
    ns = _parse([])
    r = _result("alpha")
    out = apply_scope_args(r, ns)
    summary = format_scope_summary(out)
    assert "alpha" in summary
