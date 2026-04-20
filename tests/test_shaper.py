"""Tests for streamdiff.shaper."""
import pytest

from streamdiff.schema import FieldType, SchemaField, StreamSchema
from streamdiff.shaper import (
    ShapeResult,
    get_transform,
    list_transforms,
    register_transform,
    shape_schema,
)


def _field(name: str, required: bool = True, ftype: FieldType = FieldType.STRING) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_shape_no_transforms_returns_unchanged():
    schema = _schema(_field("a"), _field("b"))
    result = shape_schema(schema, [])
    assert len(result.shaped.fields) == 2
    assert result.applied == []
    assert result.skipped == []


def test_require_all_makes_optional_required():
    schema = _schema(_field("a", required=False), _field("b", required=True))
    result = shape_schema(schema, ["require_all"])
    for f in result.shaped.fields:
        assert f.required is True


def test_require_all_only_applies_to_optional_fields():
    schema = _schema(_field("a", required=False), _field("b", required=True))
    result = shape_schema(schema, ["require_all"])
    # only the optional field "a" was changed
    assert result.applied == ["a"]


def test_optional_all_makes_required_optional():
    schema = _schema(_field("x", required=True), _field("y", required=False))
    result = shape_schema(schema, ["optional_all"])
    for f in result.shaped.fields:
        assert f.required is False
    assert result.applied == ["x"]


def test_unknown_transform_is_skipped():
    schema = _schema(_field("a"))
    result = shape_schema(schema, ["nonexistent"])
    assert "nonexistent" in result.skipped
    assert result.applied == []


def test_multiple_transforms_applied_in_order():
    schema = _schema(_field("a", required=False))
    # require_all then optional_all → net effect: optional
    result = shape_schema(schema, ["require_all", "optional_all"])
    assert result.shaped.fields[0].required is False


def test_shape_result_bool_true_when_changes():
    schema = _schema(_field("a", required=False))
    result = shape_schema(schema, ["require_all"])
    assert bool(result) is True


def test_shape_result_bool_false_when_no_changes():
    schema = _schema(_field("a", required=True))
    result = shape_schema(schema, ["require_all"])
    assert bool(result) is False


def test_to_dict_keys():
    schema = _schema(_field("a", required=False))
    result = shape_schema(schema, ["require_all"])
    d = result.to_dict()
    assert "original_count" in d
    assert "shaped_count" in d
    assert "applied" in d
    assert "skipped" in d


def test_str_representation():
    schema = _schema(_field("a", required=False))
    result = shape_schema(schema, ["require_all"])
    assert "ShapeResult" in str(result)


def test_register_and_get_custom_transform():
    register_transform("uppercase_name", lambda f: SchemaField(
        name=f.name.upper(), field_type=f.field_type, required=f.required
    ))
    fn = get_transform("uppercase_name")
    assert fn is not None
    schema = _schema(_field("hello"))
    result = shape_schema(schema, ["uppercase_name"])
    assert result.shaped.fields[0].name == "HELLO"


def test_list_transforms_includes_builtins():
    names = list_transforms()
    assert "require_all" in names
    assert "optional_all" in names
