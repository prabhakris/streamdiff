"""Tests for streamdiff.stenciler."""
import pytest
from streamdiff.schema import SchemaField, FieldType, StreamSchema
from streamdiff.stenciler import apply_stencil, apply_stencil_prefix, StencilResult


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _schema(*names: str) -> StreamSchema:
    return StreamSchema(name="test", fields=[_field(n) for n in names])


def test_apply_stencil_keeps_allowed():
    s = _schema("a", "b", "c")
    result = apply_stencil(s, {"a", "c"})
    assert [f.name for f in result.kept] == ["a", "c"]


def test_apply_stencil_drops_others():
    s = _schema("a", "b", "c")
    result = apply_stencil(s, {"a"})
    assert [f.name for f in result.dropped] == ["b", "c"]


def test_apply_stencil_original_count():
    s = _schema("x", "y", "z")
    result = apply_stencil(s, {"x"})
    assert result.original_count == 3


def test_apply_stencil_empty_allow_drops_all():
    s = _schema("a", "b")
    result = apply_stencil(s, set())
    assert result.kept == []
    assert len(result.dropped) == 2


def test_apply_stencil_all_allowed_bool_true():
    s = _schema("a", "b")
    result = apply_stencil(s, {"a", "b"})
    assert bool(result) is True


def test_apply_stencil_partial_bool_false():
    s = _schema("a", "b")
    result = apply_stencil(s, {"a"})
    assert bool(result) is False


def test_to_schema_returns_stream_schema():
    s = _schema("a", "b", "c")
    result = apply_stencil(s, {"b"})
    out = result.to_schema("masked")
    assert out.name == "masked"
    assert len(out.fields) == 1
    assert out.fields[0].name == "b"


def test_to_dict_keys():
    s = _schema("a", "b")
    d = apply_stencil(s, {"a"}).to_dict()
    assert set(d.keys()) == {"original_count", "kept", "dropped"}


def test_apply_stencil_prefix_matches():
    s = _schema("user_id", "user_name", "order_id")
    result = apply_stencil_prefix(s, ["user_"])
    assert {f.name for f in result.kept} == {"user_id", "user_name"}


def test_apply_stencil_prefix_no_match_drops_all():
    s = _schema("a", "b")
    result = apply_stencil_prefix(s, ["z_"])
    assert result.kept == []


def test_str_representation():
    s = _schema("a", "b", "c")
    r = apply_stencil(s, {"a"})
    assert "StencilResult" in str(r)
