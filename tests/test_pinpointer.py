import pytest
from streamdiff.pinpointer import pinpoint_changes, PinpointReport, Pinpoint
from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType


def _field(name, ftype=FieldType.STRING, required=True):
    return SchemaField(name=name, field_type=ftype, required=required)


def _change(name, ctype, old=None, new=None):
    return SchemaChange(field_name=name, change_type=ctype, old_field=old, new_field=new)


def _result(*changes):
    return DiffResult(changes=list(changes))


def test_no_changes_returns_empty_report():
    report = pinpoint_changes(_result())
    assert not report
    assert report.pinpoints == []


def test_added_field_pinpointed():
    f = _field("email")
    r = _result(_change("email", ChangeType.ADDED, new=f))
    report = pinpoint_changes(r)
    assert len(report.pinpoints) == 1
    p = report.pinpoints[0]
    assert p.field_name == "email"
    assert p.change_type == ChangeType.ADDED
    assert "required" in p.reason


def test_added_optional_field_reason():
    f = _field("nickname", required=False)
    r = _result(_change("nickname", ChangeType.ADDED, new=f))
    report = pinpoint_changes(r)
    assert "optional" in report.pinpoints[0].reason


def test_removed_field_pinpointed():
    f = _field("legacy")
    r = _result(_change("legacy", ChangeType.REMOVED, old=f))
    report = pinpoint_changes(r)
    p = report.pinpoints[0]
    assert p.change_type == ChangeType.REMOVED
    assert "removed" in p.reason.lower()


def test_type_changed_includes_old_and_new():
    old = _field("count", ftype=FieldType.INT)
    new = _field("count", ftype=FieldType.STRING)
    r = _result(_change("count", ChangeType.TYPE_CHANGED, old=old, new=new))
    report = pinpoint_changes(r)
    p = report.pinpoints[0]
    assert p.old_value == FieldType.INT.value
    assert p.new_value == FieldType.STRING.value


def test_required_changed_includes_values():
    old = _field("score", required=False)
    new = _field("score", required=True)
    r = _result(_change("score", ChangeType.REQUIRED_CHANGED, old=old, new=new))
    report = pinpoint_changes(r)
    p = report.pinpoints[0]
    assert p.old_value == "False"
    assert p.new_value == "True"


def test_to_dict_structure():
    f = _field("x")
    r = _result(_change("x", ChangeType.ADDED, new=f))
    report = pinpoint_changes(r)
    d = report.to_dict()
    assert "pinpoints" in d
    assert d["pinpoints"][0]["field"] == "x"


def test_str_representation():
    f = _field("y")
    p = Pinpoint(field_name="y", change_type=ChangeType.REMOVED, reason="Field was removed from schema")
    s = str(p)
    assert "y" in s
    assert "removed" in s.lower()
