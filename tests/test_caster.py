import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.caster import cast_schema, CastResult


def _field(name: str, ftype: FieldType, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_no_fields_returns_empty_result():
    s = _schema()
    result = cast_schema(s, FieldType.STRING)
    assert result.coerced == []
    assert result.skipped == []
    assert bool(result) is True


def test_same_type_not_coerced():
    s = _schema(_field("a", FieldType.STRING))
    result = cast_schema(s, FieldType.STRING)
    assert result.coerced == []
    assert result.skipped == []


def test_int_to_string_coerced():
    s = _schema(_field("x", FieldType.INT))
    result = cast_schema(s, FieldType.STRING)
    assert "x" in result.coerced
    assert result.casted.field_map["x"].field_type == FieldType.STRING


def test_int_to_long_coerced():
    s = _schema(_field("n", FieldType.INT))
    result = cast_schema(s, FieldType.LONG)
    assert "n" in result.coerced


def test_long_to_int_skipped():
    s = _schema(_field("big", FieldType.LONG))
    result = cast_schema(s, FieldType.INT)
    assert "big" in result.skipped
    assert bool(result) is False


def test_bool_to_string_coerced():
    s = _schema(_field("flag", FieldType.BOOLEAN))
    result = cast_schema(s, FieldType.STRING)
    assert "flag" in result.coerced


def test_only_filter_limits_cast():
    s = _schema(_field("a", FieldType.INT), _field("b", FieldType.INT))
    result = cast_schema(s, FieldType.STRING, only=["a"])
    assert "a" in result.coerced
    assert "b" not in result.coerced
    assert result.casted.field_map["b"].field_type == FieldType.INT


def test_only_filter_with_incompatible_skips():
    s = _schema(_field("x", FieldType.LONG))
    result = cast_schema(s, FieldType.INT, only=["x"])
    assert "x" in result.skipped


def test_original_schema_unchanged():
    s = _schema(_field("v", FieldType.INT))
    result = cast_schema(s, FieldType.STRING)
    assert s.field_map["v"].field_type == FieldType.INT


def test_to_dict_structure():
    s = _schema(_field("a", FieldType.INT), _field("b", FieldType.LONG))
    result = cast_schema(s, FieldType.STRING)
    d = result.to_dict()
    assert "coerced" in d
    assert "skipped" in d
    assert "ok" in d


def test_str_no_changes():
    s = _schema(_field("a", FieldType.STRING))
    result = cast_schema(s, FieldType.STRING)
    assert str(result) == "No casts applied."


def test_str_shows_coerced():
    s = _schema(_field("num", FieldType.INT))
    result = cast_schema(s, FieldType.STRING)
    assert "num" in str(result)
    assert "coerced" in str(result)
