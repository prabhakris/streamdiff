"""Tests for streamdiff.filter module."""

import pytest
from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType
from streamdiff.filter import (
    filter_changes,
    filter_by_field_names,
    exclude_field_names,
)


def _field(name: str, required: bool = False) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(name: str, change_type: ChangeType, required: bool = False) -> SchemaChange:
    return SchemaChange(
        field_name=name,
        change_type=change_type,
        old_field=None,
        new_field=_field(name, required),
    )


def _result(*changes: SchemaChange) -> DiffResult:
    return DiffResult(changes=list(changes))


def test_filter_no_criteria_returns_all():
    r = _result(_change("a", ChangeType.ADDED), _change("b", ChangeType.REMOVED))
    out = filter_changes(r)
    assert len(out.changes) == 2


def test_filter_by_field_name():
    r = _result(_change("a", ChangeType.ADDED), _change("b", ChangeType.ADDED))
    out = filter_changes(r, field_name="a")
    assert len(out.changes) == 1
    assert out.changes[0].field_name == "a"


def test_filter_by_change_type():
    r = _result(_change("a", ChangeType.ADDED), _change("b", ChangeType.REMOVED))
    out = filter_changes(r, change_type=ChangeType.ADDED)
    assert all(c.change_type == ChangeType.ADDED for c in out.changes)


def test_filter_breaking_only():
    breaking = SchemaChange(
        field_name="x",
        change_type=ChangeType.ADDED,
        old_field=None,
        new_field=_field("x", required=True),
    )
    safe = _change("y", ChangeType.ADDED, required=False)
    r = _result(breaking, safe)
    out = filter_changes(r, breaking_only=True)
    assert len(out.changes) == 1
    assert out.changes[0].field_name == "x"


def test_filter_by_field_names():
    r = _result(_change("a", ChangeType.ADDED), _change("b", ChangeType.ADDED), _change("c", ChangeType.REMOVED))
    out = filter_by_field_names(r, ["a", "c"])
    assert {c.field_name for c in out.changes} == {"a", "c"}


def test_exclude_field_names():
    r = _result(_change("a", ChangeType.ADDED), _change("b", ChangeType.ADDED))
    out = exclude_field_names(r, ["a"])
    assert len(out.changes) == 1
    assert out.changes[0].field_name == "b"


def test_filter_empty_result():
    r = DiffResult(changes=[])
    out = filter_changes(r, field_name="x", breaking_only=True)
    assert out.changes == []
