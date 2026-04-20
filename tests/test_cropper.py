"""Tests for streamdiff.cropper."""
import pytest

from streamdiff.schema import FieldType, SchemaField, StreamSchema
from streamdiff.cropper import CropResult, crop_schema


def _field(name: str, required: bool = True, ftype: FieldType = FieldType.STRING) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*names: str) -> StreamSchema:
    return StreamSchema(fields=[_field(n) for n in names])


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------

def test_crop_empty_schema_returns_empty():
    result = crop_schema(_schema(), limit=5)
    assert result.kept == []
    assert result.dropped == []
    assert result.original_count == 0


def test_crop_limit_larger_than_schema_keeps_all():
    schema = _schema("a", "b", "c")
    result = crop_schema(schema, limit=10)
    assert len(result.kept) == 3
    assert result.dropped == []
    assert not bool(result)  # nothing dropped


def test_crop_limit_zero_drops_all():
    schema = _schema("a", "b", "c")
    result = crop_schema(schema, limit=0)
    assert result.kept == []
    assert len(result.dropped) == 3
    assert bool(result)


def test_crop_limit_one_keeps_first():
    schema = _schema("alpha", "beta", "gamma")
    result = crop_schema(schema, limit=1)
    assert len(result.kept) == 1
    assert result.kept[0].name == "alpha"
    assert len(result.dropped) == 2


def test_crop_original_count_correct():
    schema = _schema("x", "y", "z")
    result = crop_schema(schema, limit=2)
    assert result.original_count == 3


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

def test_crop_sort_by_name_ascending():
    schema = _schema("charlie", "alpha", "bravo")
    result = crop_schema(schema, limit=2, sort_key="name")
    assert [f.name for f in result.kept] == ["alpha", "bravo"]
    assert result.dropped[0].name == "charlie"


def test_crop_sort_by_name_descending():
    schema = _schema("charlie", "alpha", "bravo")
    result = crop_schema(schema, limit=2, sort_key="name", descending=True)
    assert [f.name for f in result.kept] == ["charlie", "bravo"]


def test_crop_sort_by_type():
    fields = [
        SchemaField("b", FieldType.INTEGER, required=True),
        SchemaField("a", FieldType.STRING, required=True),
    ]
    schema = StreamSchema(fields=fields)
    result = crop_schema(schema, limit=1, sort_key="type")
    # FieldType values are strings; alphabetical order: "integer" < "string"
    assert result.kept[0].field_type == FieldType.INTEGER


def test_crop_unknown_sort_key_raises():
    with pytest.raises(ValueError, match="Unknown sort_key"):
        crop_schema(_schema("a"), limit=1, sort_key="unknown")


def test_crop_negative_limit_raises():
    with pytest.raises(ValueError, match="limit must be >= 0"):
        crop_schema(_schema("a"), limit=-1)


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def test_to_schema_returns_stream_schema():
    schema = _schema("a", "b", "c")
    result = crop_schema(schema, limit=2)
    out = result.to_schema()
    assert len(out.fields) == 2


def test_to_dict_keys():
    result = crop_schema(_schema("a", "b"), limit=1)
    d = result.to_dict()
    assert "original_count" in d
    assert "kept_count" in d
    assert "dropped_count" in d
    assert d["kept_count"] + d["dropped_count"] == d["original_count"]


def test_str_contains_ratio():
    result = crop_schema(_schema("a", "b", "c"), limit=2)
    s = str(result)
    assert "2/3" in s
