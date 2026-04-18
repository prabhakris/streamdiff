import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.differ import run_diff, DifferConfig
from streamdiff.severity import Severity
from streamdiff.diff import ChangeType


def _field(name, required=False, ftype=FieldType.STRING):
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields):
    return StreamSchema(name="test", fields=list(fields))


def test_no_changes_returns_empty():
    s = _schema(_field("a"))
    r = run_diff(s, s)
    assert r.diff.changes == []
    assert not r.has_breaking


def test_added_field_detected():
    old = _schema(_field("a"))
    new = _schema(_field("a"), _field("b"))
    r = run_diff(old, new)
    assert any(c.change_type == ChangeType.ADDED for c in r.diff.changes)


def test_removed_field_is_breaking():
    old = _schema(_field("a"), _field("b"))
    new = _schema(_field("a"))
    r = run_diff(old, new)
    assert r.has_breaking


def test_score_returned_when_requested():
    old = _schema(_field("a"))
    new = _schema(_field("a"), _field("b"))
    cfg = DifferConfig(score=True)
    r = run_diff(old, new, cfg)
    assert r.risk_score is not None


def test_score_none_by_default():
    old = _schema(_field("a"))
    new = _schema(_field("a"))
    r = run_diff(old, new)
    assert r.risk_score is None


def test_severity_filter_excludes_low():
    old = _schema(_field("a"))
    new = _schema(_field("a"), _field("b"))
    cfg = DifferConfig(min_severity=Severity.ERROR)
    r = run_diff(old, new, cfg)
    # added optional field is INFO/WARNING, not ERROR — should be filtered
    assert r.diff.changes == []


def test_include_fields_filter():
    old = _schema(_field("a"), _field("b"))
    new = _schema(_field("a"))
    cfg = DifferConfig(include_fields=["a"])
    r = run_diff(old, new, cfg)
    names = [c.field_name for c in r.diff.changes]
    assert "b" not in names
