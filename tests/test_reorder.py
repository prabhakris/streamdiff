"""Tests for streamdiff.reorder."""

import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.reorder import detect_reorder, ReorderChange, ReorderResult


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _schema(*names: str) -> StreamSchema:
    return StreamSchema(fields=[_field(n) for n in names])


def test_no_changes_returns_empty_result():
    schema = _schema("a", "b", "c")
    result = detect_reorder(schema, schema)
    assert not result
    assert result.changes == []


def test_same_order_no_changes():
    old = _schema("x", "y", "z")
    new = _schema("x", "y", "z")
    result = detect_reorder(old, new)
    assert not result


def test_swapped_fields_detected():
    old = _schema("a", "b", "c")
    new = _schema("b", "a", "c")
    result = detect_reorder(old, new)
    assert result
    names = {c.field_name for c in result.changes}
    assert "a" in names
    assert "b" in names


def test_reversed_order_all_changed():
    old = _schema("a", "b", "c")
    new = _schema("c", "b", "a")
    result = detect_reorder(old, new)
    assert result
    assert len(result.changes) == 2  # b stays at index 1


def test_added_field_ignored_in_order_check():
    old = _schema("a", "b")
    new = _schema("a", "new_field", "b")
    result = detect_reorder(old, new)
    # a and b are still in same relative order among common fields
    assert not result


def test_removed_field_ignored_in_order_check():
    old = _schema("a", "removed", "b")
    new = _schema("a", "b")
    result = detect_reorder(old, new)
    assert not result


def test_old_order_and_new_order_recorded():
    old = _schema("a", "b", "c")
    new = _schema("c", "a", "b")
    result = detect_reorder(old, new)
    assert result.old_order == ["a", "b", "c"]
    assert result.new_order == ["c", "a", "b"]


def test_to_dict_structure():
    old = _schema("a", "b")
    new = _schema("b", "a")
    result = detect_reorder(old, new)
    d = result.to_dict()
    assert "reordered" in d
    assert "old_order" in d
    assert "new_order" in d
    assert isinstance(d["reordered"], list)


def test_str_no_changes():
    schema = _schema("a", "b")
    result = detect_reorder(schema, schema)
    assert "No field order changes" in str(result)


def test_str_with_changes():
    old = _schema("a", "b")
    new = _schema("b", "a")
    result = detect_reorder(old, new)
    text = str(result)
    assert "Field order changes" in text


def test_reorder_change_to_dict():
    change = ReorderChange(field_name="foo", old_index=0, new_index=2)
    d = change.to_dict()
    assert d["field"] == "foo"
    assert d["old_index"] == 0
    assert d["new_index"] == 2


def test_reorder_change_str():
    change = ReorderChange(field_name="bar", old_index=1, new_index=3)
    assert "bar" in str(change)
    assert "1" in str(change)
    assert "3" in str(change)
