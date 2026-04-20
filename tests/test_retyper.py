"""Tests for streamdiff.retyper."""

import pytest

from streamdiff.schema import FieldType, SchemaField, StreamSchema
from streamdiff.retyper import retype_schema, RetypeResult


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_no_fields_returns_empty_result():
    schema = _schema()
    result = retype_schema(schema, {FieldType.INT: FieldType.LONG})
    assert not result
    assert result.retyped == []
    assert result.skipped == []
    assert len(result.updated.fields) == 0


def test_matching_type_is_retyped():
    schema = _schema(_field("age", FieldType.INT))
    result = retype_schema(schema, {FieldType.INT: FieldType.LONG})
    assert result
    assert len(result.retyped) == 1
    assert result.retyped[0].name == "age"
    assert result.retyped[0].field_type == FieldType.LONG


def test_non_matching_type_is_skipped():
    schema = _schema(_field("name", FieldType.STRING))
    result = retype_schema(schema, {FieldType.INT: FieldType.LONG})
    assert not result
    assert len(result.skipped) == 1
    assert result.skipped[0].name == "name"


def test_multiple_fields_mixed_types():
    schema = _schema(
        _field("age", FieldType.INT),
        _field("score", FieldType.FLOAT),
        _field("label", FieldType.STRING),
    )
    result = retype_schema(schema, {FieldType.INT: FieldType.LONG, FieldType.FLOAT: FieldType.DOUBLE})
    assert len(result.retyped) == 2
    assert len(result.skipped) == 1
    names = [f.name for f in result.retyped]
    assert "age" in names
    assert "score" in names


def test_names_filter_limits_retyping():
    schema = _schema(
        _field("age", FieldType.INT),
        _field("count", FieldType.INT),
    )
    result = retype_schema(schema, {FieldType.INT: FieldType.LONG}, names=["age"])
    assert len(result.retyped) == 1
    assert result.retyped[0].name == "age"
    # count is not in names list, so not retyped and not skipped
    count_field = result.updated.field_map.get("count")
    assert count_field is not None
    assert count_field.field_type == FieldType.INT


def test_required_flag_preserved():
    schema = _schema(_field("age", FieldType.INT, required=False))
    result = retype_schema(schema, {FieldType.INT: FieldType.LONG})
    assert result.retyped[0].required is False


def test_original_schema_unchanged():
    schema = _schema(_field("age", FieldType.INT))
    result = retype_schema(schema, {FieldType.INT: FieldType.LONG})
    assert schema.fields[0].field_type == FieldType.INT


def test_to_dict_keys():
    schema = _schema(_field("age", FieldType.INT))
    result = retype_schema(schema, {FieldType.INT: FieldType.LONG})
    d = result.to_dict()
    assert "retyped_count" in d
    assert "skipped_count" in d
    assert "retyped" in d
    assert "skipped" in d


def test_str_no_retyped():
    schema = _schema(_field("name", FieldType.STRING))
    result = retype_schema(schema, {FieldType.INT: FieldType.LONG})
    assert "No fields retyped" in str(result)


def test_str_with_retyped():
    schema = _schema(_field("age", FieldType.INT))
    result = retype_schema(schema, {FieldType.INT: FieldType.LONG})
    text = str(result)
    assert "age" in text
    assert "long" in text.lower() or "LONG" in text
