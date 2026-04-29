"""Tests for streamdiff.transposer."""
import pytest

from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.transposer import TransposeEntry, TransposeResult, transpose_schema


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_empty_schema_returns_empty_result():
    result = transpose_schema(_schema())
    assert not result
    assert result.original_field_count == 0
    assert result.entries == {}


def test_single_field_creates_one_entry():
    result = transpose_schema(_schema(_field("user_id", FieldType.STRING)))
    assert "string" in result.entries
    assert result.entries["string"].field_names == ["user_id"]
    assert result.original_field_count == 1


def test_multiple_fields_same_type_grouped():
    result = transpose_schema(_schema(
        _field("first_name", FieldType.STRING),
        _field("last_name", FieldType.STRING),
    ))
    assert len(result.entries) == 1
    assert set(result.entries["string"].field_names) == {"first_name", "last_name"}


def test_multiple_types_produce_multiple_entries():
    result = transpose_schema(_schema(
        _field("name", FieldType.STRING),
        _field("age", FieldType.INT),
        _field("score", FieldType.FLOAT),
    ))
    assert len(result.entries) == 3
    assert "string" in result.entries
    assert "int" in result.entries
    assert "float" in result.entries


def test_by_type_returns_matching_fields():
    result = transpose_schema(_schema(
        _field("a", FieldType.BOOLEAN),
        _field("b", FieldType.BOOLEAN),
        _field("c", FieldType.STRING),
    ))
    bool_fields = result.by_type("boolean")
    assert set(bool_fields) == {"a", "b"}


def test_by_type_unknown_returns_empty():
    result = transpose_schema(_schema(_field("x", FieldType.STRING)))
    assert result.by_type("int") == []


def test_to_dict_structure():
    result = transpose_schema(_schema(
        _field("id", FieldType.INT),
        _field("label", FieldType.STRING),
    ))
    d = result.to_dict()
    assert d["original_field_count"] == 2
    assert "int" in d["entries"]
    assert d["entries"]["int"] == {"type": "int", "fields": ["id"]}


def test_str_non_empty():
    result = transpose_schema(_schema(_field("x", FieldType.STRING)))
    s = str(result)
    assert "TransposeResult" in s
    assert "string" in s


def test_str_empty():
    result = transpose_schema(_schema())
    assert str(result) == "TransposeResult(empty)"


def test_bool_true_when_entries_present():
    result = transpose_schema(_schema(_field("f", FieldType.LONG)))
    assert bool(result) is True


def test_original_field_count_matches():
    fields = [_field(f"f{i}", FieldType.STRING) for i in range(5)]
    result = transpose_schema(_schema(*fields))
    assert result.original_field_count == 5
