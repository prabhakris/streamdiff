"""Tests for streamdiff.inverter."""
import pytest

from streamdiff.diff import ChangeType, SchemaChange, DiffResult
from streamdiff.schema import FieldType
from streamdiff.inverter import InvertResult, _invert_change, invert_diff


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True):
    from streamdiff.schema import SchemaField
    return SchemaField(name=name, field_type=ftype, required=required)


def _change(
    name: str,
    change_type: ChangeType,
    old_type: FieldType = None,
    new_type: FieldType = None,
) -> SchemaChange:
    return SchemaChange(
        field_name=name,
        change_type=change_type,
        old_type=old_type,
        new_type=new_type,
    )


def _result(*changes: SchemaChange) -> DiffResult:
    return DiffResult(changes=list(changes))


def test_invert_added_becomes_removed():
    c = _change("foo", ChangeType.ADDED, new_type=FieldType.STRING)
    inv = _invert_change(c)
    assert inv.change_type == ChangeType.REMOVED
    assert inv.old_type == FieldType.STRING
    assert inv.new_type is None
    assert inv.field_name == "foo"


def test_invert_removed_becomes_added():
    c = _change("bar", ChangeType.REMOVED, old_type=FieldType.INT)
    inv = _invert_change(c)
    assert inv.change_type == ChangeType.ADDED
    assert inv.new_type == FieldType.INT
    assert inv.old_type is None


def test_invert_type_changed_swaps_types():
    c = _change("baz", ChangeType.TYPE_CHANGED, old_type=FieldType.INT, new_type=FieldType.STRING)
    inv = _invert_change(c)
    assert inv.change_type == ChangeType.TYPE_CHANGED
    assert inv.old_type == FieldType.STRING
    assert inv.new_type == FieldType.INT


def test_invert_diff_empty_result():
    result = _result()
    inv = invert_diff(result)
    assert isinstance(inv, InvertResult)
    assert not inv
    assert inv.changes == []


def test_invert_diff_multiple_changes():
    result = _result(
        _change("a", ChangeType.ADDED, new_type=FieldType.STRING),
        _change("b", ChangeType.REMOVED, old_type=FieldType.INT),
    )
    inv = invert_diff(result)
    assert len(inv.changes) == 2
    assert inv.changes[0].change_type == ChangeType.REMOVED
    assert inv.changes[1].change_type == ChangeType.ADDED


def test_invert_result_to_dict():
    result = _result(_change("x", ChangeType.ADDED, new_type=FieldType.BOOLEAN))
    inv = invert_diff(result)
    d = inv.to_dict()
    assert d["total"] == 1
    assert d["changes"][0]["change_type"] == ChangeType.REMOVED.value
    assert d["changes"][0]["field"] == "x"


def test_invert_result_str_no_changes():
    inv = InvertResult(changes=[])
    assert "no changes" in str(inv)


def test_invert_result_str_with_changes():
    result = _result(_change("y", ChangeType.REMOVED, old_type=FieldType.FLOAT))
    inv = invert_diff(result)
    s = str(inv)
    assert "y" in s
    assert "added" in s.lower()
