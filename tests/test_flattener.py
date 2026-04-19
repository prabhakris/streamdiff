import pytest
from streamdiff.schema import SchemaField, StreamSchema, FieldType
from streamdiff.flattener import (
    FlatField, FlatSchema, flatten_schema, diff_flat_schemas
)


def _field(name, ftype=FieldType.STRING, required=True):
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(name, fields):
    s = StreamSchema(name=name)
    for f in fields:
        s.fields[f.name] = f
    return s


def test_flatten_empty_schema():
    s = _schema("empty", [])
    result = flatten_schema(s)
    assert result.name == "empty"
    assert result.fields == []


def test_flatten_single_field():
    s = _schema("s", [_field("user_id")])
    result = flatten_schema(s)
    assert len(result.fields) == 1
    assert result.fields[0].path == "user_id"
    assert result.fields[0].field_type == FieldType.STRING


def test_flatten_multiple_fields():
    s = _schema("s", [_field("a"), _field("b", FieldType.INTEGER)])
    result = flatten_schema(s)
    paths = [f.path for f in result.fields]
    assert "a" in paths
    assert "b" in paths


def test_by_path_returns_dict():
    s = _schema("s", [_field("x"), _field("y")])
    flat = flatten_schema(s)
    bp = flat.by_path()
    assert "x" in bp
    assert "y" in bp
    assert isinstance(bp["x"], FlatField)


def test_to_dict_structure():
    s = _schema("s", [_field("f1")])
    flat = flatten_schema(s)
    d = flat.to_dict()
    assert d["name"] == "s"
    assert len(d["fields"]) == 1
    assert d["fields"][0]["path"] == "f1"


def test_flat_field_str():
    ff = FlatField(path="a.b", field_type=FieldType.STRING, required=True)
    assert "a.b" in str(ff)
    assert "required" in str(ff)


def test_diff_flat_added():
    old = _schema("s", [_field("a")])
    new = _schema("s", [_field("a"), _field("b")])
    result = diff_flat_schemas(flatten_schema(old), flatten_schema(new))
    assert "b" in result["added"]
    assert result["removed"] == []


def test_diff_flat_removed():
    old = _schema("s", [_field("a"), _field("b")])
    new = _schema("s", [_field("a")])
    result = diff_flat_schemas(flatten_schema(old), flatten_schema(new))
    assert "b" in result["removed"]


def test_diff_flat_type_changed():
    old = _schema("s", [_field("x", FieldType.STRING)])
    new = _schema("s", [_field("x", FieldType.INTEGER)])
    result = diff_flat_schemas(flatten_schema(old), flatten_schema(new))
    assert "x" in result["type_changed"]


def test_diff_flat_no_changes():
    s = _schema("s", [_field("a"), _field("b")])
    result = diff_flat_schemas(flatten_schema(s), flatten_schema(s))
    assert result == {"added": [], "removed": [], "type_changed": []}
