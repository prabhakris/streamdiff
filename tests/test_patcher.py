"""Tests for streamdiff.patcher."""

import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.patcher import apply_patch, patch_summary


def _field(name, ftype=FieldType.STRING, required=True):
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields):
    return StreamSchema(name="test", fields=list(fields))


def _result(*changes):
    return DiffResult(changes=list(changes))


def test_apply_patch_no_changes():
    schema = _schema(_field("id"), _field("name"))
    result = _result()
    patched = apply_patch(schema, result)
    assert {f.name for f in patched.fields} == {"id", "name"}


def test_apply_patch_adds_field():
    base = _schema(_field("id"))
    new_f = _field("email")
    change = SchemaChange(
        field_name="email",
        change_type=ChangeType.ADDED,
        old_field=None,
        new_field=new_f,
    )
    patched = apply_patch(base, _result(change))
    names = {f.name for f in patched.fields}
    assert "email" in names
    assert "id" in names


def test_apply_patch_removes_field():
    base = _schema(_field("id"), _field("deprecated"))
    change = SchemaChange(
        field_name="deprecated",
        change_type=ChangeType.REMOVED,
        old_field=_field("deprecated"),
        new_field=None,
    )
    patched = apply_patch(base, _result(change))
    assert "deprecated" not in {f.name for f in patched.fields}


def test_apply_patch_type_changed():
    old_f = _field("count", FieldType.INT)
    new_f = _field("count", FieldType.LONG)
    base = _schema(old_f)
    change = SchemaChange(
        field_name="count",
        change_type=ChangeType.TYPE_CHANGED,
        old_field=old_f,
        new_field=new_f,
    )
    patched = apply_patch(base, _result(change))
    patched_map = {f.name: f for f in patched.fields}
    assert patched_map["count"].field_type == FieldType.LONG


def test_patch_summary_no_changes():
    lines = patch_summary(_result())
    assert lines == ["no changes to apply"]


def test_patch_summary_add_remove():
    changes = [
        SchemaChange(field_name="x", change_type=ChangeType.ADDED, old_field=None, new_field=_field("x")),
        SchemaChange(field_name="y", change_type=ChangeType.REMOVED, old_field=_field("y"), new_field=None),
    ]
    lines = patch_summary(_result(*changes))
    assert any("add field 'x'" in l for l in lines)
    assert any("remove field 'y'" in l for l in lines)
