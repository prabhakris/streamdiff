import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.extractor import (
    ExtractResult,
    extract_by_names,
    extract_by_pattern,
    extract_by_type,
)


def _field(name: str, ftype: str = "string", required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType(ftype), required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_extract_by_names_keeps_matching():
    s = _schema(_field("a"), _field("b"), _field("c"))
    result = extract_by_names(s, ["a", "c"])
    assert [f.name for f in result.extracted] == ["a", "c"]
    assert [f.name for f in result.dropped] == ["b"]


def test_extract_by_names_none_match_returns_empty():
    s = _schema(_field("x"), _field("y"))
    result = extract_by_names(s, ["z"])
    assert result.extracted == []
    assert len(result.dropped) == 2
    assert not result


def test_extract_by_names_original_count():
    s = _schema(_field("a"), _field("b"))
    result = extract_by_names(s, ["a"])
    assert result.original_count == 2


def test_extract_by_pattern_wildcard():
    s = _schema(_field("user_id"), _field("user_name"), _field("order_id"))
    result = extract_by_pattern(s, "user_*")
    assert [f.name for f in result.extracted] == ["user_id", "user_name"]
    assert [f.name for f in result.dropped] == ["order_id"]


def test_extract_by_pattern_no_match():
    s = _schema(_field("alpha"), _field("beta"))
    result = extract_by_pattern(s, "gamma_*")
    assert result.extracted == []
    assert not result


def test_extract_by_pattern_all_match():
    s = _schema(_field("foo_a"), _field("foo_b"))
    result = extract_by_pattern(s, "foo_*")
    assert len(result.extracted) == 2
    assert result.dropped == []


def test_extract_by_type_returns_matching():
    s = _schema(_field("a", "string"), _field("b", "integer"), _field("c", "string"))
    result = extract_by_type(s, "string")
    assert [f.name for f in result.extracted] == ["a", "c"]
    assert [f.name for f in result.dropped] == ["b"]


def test_extract_by_type_no_match():
    s = _schema(_field("a", "string"))
    result = extract_by_type(s, "boolean")
    assert result.extracted == []
    assert not result


def test_to_schema_produces_stream_schema():
    s = _schema(_field("a"), _field("b"))
    result = extract_by_names(s, ["a"])
    out = result.to_schema(name="subset")
    assert out.name == "subset"
    assert len(out.fields) == 1
    assert out.fields[0].name == "a"


def test_to_dict_keys():
    s = _schema(_field("a"), _field("b"))
    result = extract_by_names(s, ["a"])
    d = result.to_dict()
    assert "original_count" in d
    assert "extracted_count" in d
    assert "dropped_count" in d
    assert d["extracted_count"] == 1
    assert d["dropped_count"] == 1


def test_str_representation():
    s = _schema(_field("a"))
    result = extract_by_names(s, ["a"])
    assert "ExtractResult" in str(result)
