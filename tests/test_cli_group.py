"""Tests for streamdiff.cli_group."""
import argparse
import pytest
from streamdiff.diff import SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType
from streamdiff.cli_group import add_group_args, apply_grouping


def _field(name: str) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=False)


def _change(name: str, ct: ChangeType = ChangeType.ADDED) -> SchemaChange:
    return SchemaChange(field_name=name, change_type=ct, field=_field(name))


def _parse(args):
    parser = argparse.ArgumentParser()
    add_group_args(parser)
    return parser.parse_args(args)


def test_add_group_args_default_none():
    ns = _parse([])
    assert ns.group_by is None
    assert ns.group_separator == "."


def test_add_group_args_prefix():
    ns = _parse(["--group-by", "prefix"])
    assert ns.group_by == "prefix"


def test_add_group_args_change_type():
    ns = _parse(["--group-by", "change_type"])
    assert ns.group_by == "change_type"


def test_add_group_args_custom_separator():
    ns = _parse(["--group-by", "prefix", "--group-separator", "_"])
    assert ns.group_by == "prefix"
    assert ns.group_separator == "_"


def test_apply_grouping_no_group_by_does_nothing(capsys):
    ns = _parse([])
    apply_grouping(ns, [_change("a")])
    captured = capsys.readouterr()
    assert captured.out == ""


def test_apply_grouping_by_prefix(capsys):
    ns = _parse(["--group-by", "prefix"])
    changes = [_change("user.name"), _change("user.age"), _change("order.id")]
    apply_grouping(ns, changes)
    out = capsys.readouterr().out
    assert "user" in out
    assert "order" in out


def test_apply_grouping_by_change_type(capsys):
    ns = _parse(["--group-by", "change_type"])
    changes = [_change("a", ChangeType.ADDED), _change("b", ChangeType.REMOVED)]
    apply_grouping(ns, changes)
    out = capsys.readouterr().out
    assert "added" in out.lower() or "ADDED" in out


def test_apply_grouping_empty_changes_produces_no_output(capsys):
    """Grouping an empty list of changes should not produce any output."""
    ns = _parse(["--group-by", "prefix"])
    apply_grouping(ns, [])
    out = capsys.readouterr().out
    assert out == ""
