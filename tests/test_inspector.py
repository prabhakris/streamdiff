import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.inspector import (
    FieldInspection,
    inspect_field,
    inspect_all,
)


def _field(name: str, ftype=FieldType.STRING, required=True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_inspect_field_stable():
    f = _field("id")
    old = _schema(f)
    new = _schema(f)
    result = inspect_field("id", old, new)
    assert result is not None
    assert result.status() == "stable"
    assert result.present_in_old is True
    assert result.present_in_new is True


def test_inspect_field_added():
    old = _schema()
    new = _schema(_field("name"))
    result = inspect_field("name", old, new)
    assert result is not None
    assert result.status() == "added"
    assert result.present_in_old is False
    assert result.present_in_new is True


def test_inspect_field_removed():
    old = _schema(_field("age", FieldType.INTEGER))
    new = _schema()
    result = inspect_field("age", old, new)
    assert result is not None
    assert result.status() == "removed"
    assert result.field_type == FieldType.INTEGER


def test_inspect_field_not_present_returns_none():
    old = _schema(_field("x"))
    new = _schema(_field("x"))
    result = inspect_field("missing", old, new)
    assert result is None


def test_inspect_field_uses_new_metadata_when_available():
    old = _schema(_field("score", FieldType.INTEGER, required=True))
    new = _schema(_field("score", FieldType.FLOAT, required=False))
    result = inspect_field("score", old, new)
    assert result.field_type == FieldType.FLOAT
    assert result.required is False


def test_inspect_all_returns_all_names():
    old = _schema(_field("a"), _field("b"))
    new = _schema(_field("b"), _field("c"))
    results = inspect_all(old, new)
    names = [r.name for r in results]
    assert names == ["a", "b", "c"]


def test_inspect_all_statuses():
    old = _schema(_field("a"), _field("b"))
    new = _schema(_field("b"), _field("c"))
    by_name = {r.name: r for r in inspect_all(old, new)}
    assert by_name["a"].status() == "removed"
    assert by_name["b"].status() == "stable"
    assert by_name["c"].status() == "added"


def test_to_dict_keys():
    f = _field("user_id")
    result = inspect_field("user_id", _schema(f), _schema(f))
    d = result.to_dict()
    assert set(d.keys()) == {"name", "type", "required", "present_in_old", "present_in_new", "status"}


def test_str_representation():
    f = _field("email", FieldType.STRING, required=False)
    result = inspect_field("email", _schema(), _schema(f))
    s = str(result)
    assert "email" in s
    assert "optional" in s
    assert "added" in s
