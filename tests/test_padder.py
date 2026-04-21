"""Tests for streamdiff.padder."""

import pytest

from streamdiff.schema import FieldType, SchemaField, StreamSchema
from streamdiff.padder import pad_schema, PadResult


def _field(name: str, required: bool = True, ftype: FieldType = FieldType.STRING) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*names: str) -> StreamSchema:
    return StreamSchema(name="test", fields=[_field(n) for n in names])


# ---------------------------------------------------------------------------
# pad_schema
# ---------------------------------------------------------------------------

def test_pad_empty_schema_to_three():
    result = pad_schema(_schema(), target=3)
    assert len(result.schema.fields) == 3
    assert result.original_count == 0
    assert result.target_count == 3
    assert len(result.added_fields) == 3


def test_pad_adds_correct_number_of_fields():
    result = pad_schema(_schema("a", "b"), target=5)
    assert len(result.schema.fields) == 5
    assert len(result.added_fields) == 3


def test_pad_target_equal_to_current_no_change():
    result = pad_schema(_schema("x", "y"), target=2)
    assert not result
    assert result.original_count == 2
    assert result.target_count == 2
    assert result.added_fields == []


def test_pad_target_less_than_current_no_change():
    result = pad_schema(_schema("a", "b", "c"), target=1)
    assert not result
    assert len(result.schema.fields) == 3


def test_pad_uses_custom_prefix():
    result = pad_schema(_schema(), target=2, prefix="extra")
    names = [f.name for f in result.added_fields]
    assert all(n.startswith("extra_") for n in names)


def test_pad_default_fields_are_optional():
    result = pad_schema(_schema(), target=2)
    for f in result.added_fields:
        assert f.required is False


def test_pad_required_flag_respected():
    result = pad_schema(_schema(), target=2, required=True)
    for f in result.added_fields:
        assert f.required is True


def test_pad_uses_custom_field_type():
    result = pad_schema(_schema(), target=2, field_type=FieldType.INTEGER)
    for f in result.added_fields:
        assert f.field_type == FieldType.INTEGER


def test_pad_no_duplicate_names():
    result = pad_schema(_schema("pad_field_1"), target=3, prefix="pad_field")
    all_names = [f.name for f in result.schema.fields]
    assert len(all_names) == len(set(all_names))


def test_bool_true_when_fields_added():
    result = pad_schema(_schema(), target=1)
    assert bool(result) is True


def test_bool_false_when_no_fields_added():
    result = pad_schema(_schema("a"), target=1)
    assert bool(result) is False


def test_to_dict_keys():
    result = pad_schema(_schema("a"), target=3)
    d = result.to_dict()
    assert "original_count" in d
    assert "target_count" in d
    assert "added_count" in d
    assert "added_fields" in d
    assert "schema_fields" in d


def test_str_no_padding():
    result = pad_schema(_schema("a"), target=1)
    assert "No padding" in str(result)


def test_str_with_padding():
    result = pad_schema(_schema(), target=2)
    assert "Padded" in str(result)
    assert "->" in str(result)
