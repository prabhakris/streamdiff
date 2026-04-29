"""Tests for streamdiff.rotator."""
import pytest

from streamdiff.schema import FieldType, SchemaField, StreamSchema
from streamdiff.rotator import rotate_schema, RotateResult


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _schema(*names: str) -> StreamSchema:
    return StreamSchema(name="test", fields=[_field(n) for n in names])


# ---------------------------------------------------------------------------
# rotate_schema
# ---------------------------------------------------------------------------

def test_rotate_empty_schema_returns_empty():
    s = _schema()
    result = rotate_schema(s, offset=1)
    assert result.total == 0
    assert result.rotated.fields == []


def test_rotate_offset_zero_keeps_order():
    s = _schema("a", "b", "c")
    result = rotate_schema(s, offset=0)
    assert [f.name for f in result.rotated.fields] == ["a", "b", "c"]


def test_rotate_offset_one():
    s = _schema("a", "b", "c")
    result = rotate_schema(s, offset=1)
    assert [f.name for f in result.rotated.fields] == ["b", "c", "a"]


def test_rotate_offset_two():
    s = _schema("a", "b", "c")
    result = rotate_schema(s, offset=2)
    assert [f.name for f in result.rotated.fields] == ["c", "a", "b"]


def test_rotate_offset_equals_length_is_identity():
    s = _schema("a", "b", "c")
    result = rotate_schema(s, offset=3)
    assert [f.name for f in result.rotated.fields] == ["a", "b", "c"]


def test_rotate_offset_larger_than_length_wraps():
    s = _schema("a", "b", "c")
    result = rotate_schema(s, offset=5)  # 5 % 3 == 2
    assert [f.name for f in result.rotator.fields] == ["c", "a", "b"] if False else True
    # correct assertion:
    assert [f.name for f in result.rotated.fields] == ["c", "a", "b"]


def test_rotate_bool_true_when_effective_offset_nonzero():
    s = _schema("a", "b", "c")
    result = rotate_schema(s, offset=1)
    assert bool(result) is True


def test_rotate_bool_false_when_effective_offset_zero():
    s = _schema("a", "b", "c")
    result = rotate_schema(s, offset=3)
    assert bool(result) is False


def test_rotate_to_dict_contains_fields():
    s = _schema("x", "y")
    result = rotate_schema(s, offset=1)
    d = result.to_dict()
    assert d["offset"] == 1
    assert d["total"] == 2
    assert [f["name"] for f in d["fields"]] == ["y", "x"]


def test_rotate_str_contains_offset():
    s = _schema("a", "b")
    result = rotate_schema(s, offset=1)
    text = str(result)
    assert "offset=1" in text
    assert "b" in text


def test_rotate_preserves_schema_name():
    s = StreamSchema(name="my_stream", fields=[_field("a")])
    result = rotate_schema(s, offset=1)
    assert result.rotated.name == "my_stream"
