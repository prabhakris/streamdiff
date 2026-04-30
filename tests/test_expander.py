"""Tests for streamdiff.expander."""
import pytest

from streamdiff.schema import FieldType, SchemaField, StreamSchema
from streamdiff.expander import expand_schema, ExpandResult


def _field(name: str, ftype: FieldType, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


# ---------------------------------------------------------------------------
# expand_schema
# ---------------------------------------------------------------------------

def test_empty_schema_returns_empty_result():
    result = expand_schema(_schema())
    assert not result
    assert len(result.expanded.fields) == 0


def test_no_promotable_fields_returns_unchanged():
    schema = _schema(_field("label", FieldType.STRING))
    result = expand_schema(schema)
    assert not result
    assert len(result.expanded.fields) == 1


def test_int_field_gets_wide_variant():
    schema = _schema(_field("count", FieldType.INT))
    result = expand_schema(schema)
    assert result
    names = [f.name for f in result.expanded.fields]
    assert "count" in names
    assert "count_wide" in names


def test_float_field_gets_wide_variant():
    schema = _schema(_field("ratio", FieldType.FLOAT))
    result = expand_schema(schema)
    assert result
    names = [f.name for f in result.expanded.fields]
    assert "ratio_wide" in names


def test_promoted_field_is_optional():
    schema = _schema(_field("count", FieldType.INT, required=True))
    result = expand_schema(schema)
    wide = next(f for f in result.expanded.fields if f.name == "count_wide")
    assert wide.required is False


def test_promoted_field_has_correct_type():
    schema = _schema(_field("count", FieldType.INT))
    result = expand_schema(schema)
    wide = next(f for f in result.expanded.fields if f.name == "count_wide")
    assert wide.field_type == FieldType.LONG


def test_float_promoted_to_double():
    schema = _schema(_field("ratio", FieldType.FLOAT))
    result = expand_schema(schema)
    wide = next(f for f in result.expanded.fields if f.name == "ratio_wide")
    assert wide.field_type == FieldType.DOUBLE


def test_custom_suffix():
    schema = _schema(_field("age", FieldType.INT))
    result = expand_schema(schema, suffix="_promoted")
    names = [f.name for f in result.expanded.fields]
    assert "age_promoted" in names
    assert "age_wide" not in names


def test_promote_types_false_skips_promotion():
    schema = _schema(_field("count", FieldType.INT))
    result = expand_schema(schema, promote_types=False)
    assert not result
    assert len(result.expanded.fields) == 1


def test_existing_wide_name_not_duplicated():
    schema = _schema(_field("val", FieldType.INT), _field("val_wide", FieldType.LONG))
    result = expand_schema(schema)
    names = [f.name for f in result.expanded.fields]
    assert names.count("val_wide") == 1


def test_to_dict_keys():
    schema = _schema(_field("n", FieldType.INT))
    result = expand_schema(schema)
    d = result.to_dict()
    assert "original_count" in d
    assert "expanded_count" in d
    assert "added" in d


def test_str_no_additions():
    result = expand_schema(_schema())
    assert "no fields added" in str(result)


def test_str_with_additions():
    schema = _schema(_field("x", FieldType.INT))
    result = expand_schema(schema)
    assert "x_wide" in str(result)
