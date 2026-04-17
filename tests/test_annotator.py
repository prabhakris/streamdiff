import pytest
from streamdiff.annotator import annotate, annotate_all, AnnotatedChange
from streamdiff.diff import SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType


def _field(name="f", ftype=FieldType.STRING, required=False):
    return SchemaField(name=name, field_type=ftype, required=required)


def _change(change_type, old=None, new=None):
    return SchemaChange(change_type=change_type, old_field=old, new_field=new)


def test_annotate_added_field():
    f = _field("email", required=False)
    c = _change(ChangeType.ADDED, new=f)
    result = annotate(c)
    assert isinstance(result, AnnotatedChange)
    assert "email" in result.description
    assert "added" in result.description
    assert "optional" in result.description
    assert result.hint != ""


def test_annotate_removed_field():
    f = _field("old_col")
    c = _change(ChangeType.REMOVED, old=f)
    result = annotate(c)
    assert "old_col" in result.description
    assert "removed" in result.description
    assert "break" in result.hint


def test_annotate_type_changed():
    old = _field("count", ftype=FieldType.INT)
    new = _field("count", ftype=FieldType.STRING)
    c = _change(ChangeType.TYPE_CHANGED, old=old, new=new)
    result = annotate(c)
    assert "count" in result.description
    assert "int" in result.description
    assert "string" in result.description


def test_annotate_required_changed():
    old = _field("x", required=False)
    new = _field("x", required=True)
    c = _change(ChangeType.REQUIRED_CHANGED, old=old, new=new)
    result = annotate(c)
    assert "x" in result.description
    assert "required" in result.description


def test_annotate_all_returns_list():
    changes = [
        _change(ChangeType.ADDED, new=_field("a")),
        _change(ChangeType.REMOVED, old=_field("b")),
    ]
    results = annotate_all(changes)
    assert len(results) == 2
    assert all(isinstance(r, AnnotatedChange) for r in results)


def test_annotate_all_empty():
    assert annotate_all([]) == []


def test_str_representation():
    f = _field("z")
    c = _change(ChangeType.REMOVED, old=f)
    result = annotate(c)
    s = str(result)
    assert " — " in s
