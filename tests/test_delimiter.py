"""Tests for streamdiff.delimiter."""
import pytest

from streamdiff.schema import FieldType, SchemaField, StreamSchema
from streamdiff.delimiter import delimit_schema, DelimitResult


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _schema(*names: str) -> StreamSchema:
    return StreamSchema(name="test", fields=[_field(n) for n in names])


def test_empty_schema_returns_empty_result():
    result = delimit_schema(_schema())
    assert not result
    assert result.chunks == {}
    assert result.unmatched == []
    assert result.original_count == 0


def test_fields_without_delimiter_go_to_unmatched():
    result = delimit_schema(_schema("foo", "bar", "baz"))
    assert result.chunks == {}
    assert len(result.unmatched) == 3


def test_fields_with_delimiter_grouped_by_prefix():
    result = delimit_schema(_schema("user.id", "user.name", "order.id"))
    assert set(result.chunks.keys()) == {"user", "order"}
    assert len(result.chunks["user"]) == 2
    assert len(result.chunks["order"]) == 1
    assert result.unmatched == []


def test_mixed_fields_split_correctly():
    result = delimit_schema(_schema("user.id", "plain", "order.total"))
    assert set(result.chunks.keys()) == {"user", "order"}
    assert len(result.unmatched) == 1
    assert result.unmatched[0].name == "plain"


def test_custom_delimiter():
    result = delimit_schema(_schema("user_id", "user_name", "order_id"), delimiter="_")
    assert set(result.chunks.keys()) == {"user", "order"}


def test_depth_two_groups_by_two_segments():
    result = delimit_schema(
        _schema("a.b.c", "a.b.d", "a.x.y", "top"),
        delimiter=".",
        depth=2,
    )
    assert "a.b" in result.chunks
    assert "a.x" in result.chunks
    assert len(result.chunks["a.b"]) == 2
    assert result.unmatched[0].name == "top"


def test_bool_true_when_chunks_present():
    result = delimit_schema(_schema("a.b"))
    assert bool(result) is True


def test_bool_false_when_no_chunks():
    result = delimit_schema(_schema("plain"))
    assert bool(result) is False


def test_to_dict_structure():
    result = delimit_schema(_schema("user.id", "plain"))
    d = result.to_dict()
    assert d["delimiter"] == "."
    assert d["original_count"] == 2
    assert d["unmatched_count"] == 1
    assert "user" in d["chunks"]


def test_str_representation():
    result = delimit_schema(_schema("user.id", "plain"))
    s = str(result)
    assert "user" in s
    assert "unmatched" in s
