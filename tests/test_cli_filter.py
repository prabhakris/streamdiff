"""Integration-level tests for CLI filter argument wiring."""

import argparse
import pytest
from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType
from streamdiff.cli_filter import add_filter_args, apply_filter_args


def _field(name: str, required: bool = False) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(name: str, ct: ChangeType, required: bool = False) -> SchemaChange:
    return SchemaChange(field_name=name, change_type=ct, old_field=None, new_field=_field(name, required))


def _parse(argv):
    parser = argparse.ArgumentParser()
    add_filter_args(parser)
    return parser.parse_args(argv)


def _result(*changes):
    return DiffResult(changes=list(changes))


def test_no_filters_returns_all():
    args = _parse([])
    r = _result(_change("a", ChangeType.ADDED), _change("b", ChangeType.REMOVED))
    out = apply_filter_args(args, r)
    assert len(out.changes) == 2


def test_field_filter():
    args = _parse(["--field", "a"])
    r = _result(_change("a", ChangeType.ADDED), _change("b", ChangeType.ADDED))
    out = apply_filter_args(args, r)
    assert [c.field_name for c in out.changes] == ["a"]


def test_change_type_filter():
    args = _parse(["--change-type", "removed"])
    r = _result(_change("a", ChangeType.ADDED), _change("b", ChangeType.REMOVED))
    out = apply_filter_args(args, r)
    assert all(c.change_type == ChangeType.REMOVED for c in out.changes)


def test_breaking_only_filter():
    args = _parse(["--breaking-only"])
    breaking = SchemaChange(field_name="x", change_type=ChangeType.ADDED, old_field=None, new_field=_field("x", required=True))
    safe = _change("y", ChangeType.ADDED, required=False)
    r = _result(breaking, safe)
    out = apply_filter_args(args, r)
    assert len(out.changes) == 1 and out.changes[0].field_name == "x"


def test_include_fields():
    args = _parse(["--include-fields", "a,c"])
    r = _result(_change("a", ChangeType.ADDED), _change("b", ChangeType.ADDED), _change("c", ChangeType.REMOVED))
    out = apply_filter_args(args, r)
    assert {c.field_name for c in out.changes} == {"a", "c"}


def test_exclude_fields():
    args = _parse(["--exclude-fields", "b"])
    r = _result(_change("a", ChangeType.ADDED), _change("b", ChangeType.ADDED))
    out = apply_filter_args(args, r)
    assert [c.field_name for c in out.changes] == ["a"]
