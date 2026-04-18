import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.profiler import profile_schema, FieldStat, ProfileResult


def _field(name, ftype=FieldType.STRING, required=True):
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields):
    return StreamSchema(name="test", fields=list(fields))


def test_empty_schema():
    result = profile_schema(_schema())
    assert result.total_fields == 0
    assert result.required_count == 0
    assert result.optional_count == 0
    assert result.max_depth == 0
    assert result.type_counts == {}


def test_counts_required_and_optional():
    s = _schema(
        _field("a", required=True),
        _field("b", required=False),
        _field("c", required=False),
    )
    r = profile_schema(s)
    assert r.total_fields == 3
    assert r.required_count == 1
    assert r.optional_count == 2


def test_type_counts():
    s = _schema(
        _field("a", FieldType.STRING),
        _field("b", FieldType.INT),
        _field("c", FieldType.STRING),
    )
    r = profile_schema(s)
    assert r.type_counts["string"] == 2
    assert r.type_counts["int"] == 1


def test_depth_flat():
    s = _schema(_field("foo"), _field("bar"))
    r = profile_schema(s)
    assert r.max_depth == 1


def test_depth_nested():
    s = _schema(_field("a.b.c"), _field("x"))
    r = profile_schema(s)
    assert r.max_depth == 3


def test_to_dict_keys():
    s = _schema(_field("id", FieldType.INT))
    d = profile_schema(s).to_dict()
    assert "schema_name" in d
    assert "total_fields" in d
    assert "fields" in d
    assert d["fields"][0]["name"] == "id"


def test_schema_name_preserved():
    schema = StreamSchema(name="orders_v2", fields=[_field("id")])
    r = profile_schema(schema)
    assert r.schema_name == "orders_v2"
