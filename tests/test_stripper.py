"""Tests for streamdiff.stripper."""
import pytest

from streamdiff.schema import FieldType, SchemaField, StreamSchema
from streamdiff.stripper import StripResult, strip_by_names, strip_required


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(fields=list(fields))


# ---------------------------------------------------------------------------
# strip_required
# ---------------------------------------------------------------------------

def test_strip_required_empty_schema():
    result = strip_required(_schema())
    assert result.original_count == 0
    assert result.stripped_fields == []
    assert "required" in result.removed_attrs


def test_strip_required_makes_all_optional():
    schema = _schema(_field("a", required=True), _field("b", required=False))
    result = strip_required(schema)
    assert all(not f.required for f in result.stripped_fields)


def test_strip_required_preserves_names_and_types():
    schema = _schema(_field("x"), _field("y"))
    result = strip_required(schema)
    names = [f.name for f in result.stripped_fields]
    assert names == ["x", "y"]


def test_strip_required_original_count():
    schema = _schema(_field("a"), _field("b"), _field("c"))
    result = strip_required(schema)
    assert result.original_count == 3
    assert len(result.stripped_fields) == 3


def test_strip_required_bool_true_when_fields_present():
    result = strip_required(_schema(_field("a")))
    assert bool(result) is True


def test_strip_required_bool_false_when_empty():
    result = strip_required(_schema())
    assert bool(result) is False


# ---------------------------------------------------------------------------
# strip_by_names
# ---------------------------------------------------------------------------

def test_strip_by_names_removes_matching():
    schema = _schema(_field("a"), _field("b"), _field("c"))
    result = strip_by_names(schema, {"b"})
    names = [f.name for f in result.stripped_fields]
    assert names == ["a", "c"]


def test_strip_by_names_no_match_keeps_all():
    schema = _schema(_field("a"), _field("b"))
    result = strip_by_names(schema, {"z"})
    assert len(result.stripped_fields) == 2


def test_strip_by_names_empty_set_keeps_all():
    schema = _schema(_field("a"), _field("b"))
    result = strip_by_names(schema, set())
    assert len(result.stripped_fields) == 2
    assert result.removed_attrs == set()


def test_strip_by_names_original_count():
    schema = _schema(_field("a"), _field("b"), _field("c"))
    result = strip_by_names(schema, {"a", "c"})
    assert result.original_count == 3
    assert len(result.stripped_fields) == 1


# ---------------------------------------------------------------------------
# to_dict / __str__ / to_schema
# ---------------------------------------------------------------------------

def test_to_dict_keys():
    schema = _schema(_field("a"), _field("b"))
    result = strip_required(schema)
    d = result.to_dict()
    assert set(d.keys()) == {"original_count", "stripped_count", "removed_attrs", "fields"}


def test_str_non_empty():
    schema = _schema(_field("a"))
    result = strip_required(schema)
    assert "StripResult" in str(result)
    assert "required" in str(result)


def test_str_empty():
    result = strip_required(_schema())
    assert "no fields" in str(result)


def test_to_schema_returns_stream_schema():
    schema = _schema(_field("a"), _field("b"))
    result = strip_required(schema)
    new_schema = result.to_schema()
    assert isinstance(new_schema, StreamSchema)
    assert len(new_schema.fields) == 2
