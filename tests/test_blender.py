"""Tests for streamdiff.blender."""
import pytest

from streamdiff.schema import FieldType, SchemaField, StreamSchema
from streamdiff.blender import BlendConflict, BlendResult, blend_schemas


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField, name: str = "test") -> StreamSchema:
    return StreamSchema(name=name, fields=list(fields))


# ---------------------------------------------------------------------------
# blend_schemas
# ---------------------------------------------------------------------------

def test_blend_disjoint_schemas_combines_all_fields():
    left = _schema(_field("id"), _field("name"))
    right = _schema(_field("email"), _field("age", FieldType.INTEGER))
    result = blend_schemas(left, right)
    names = {f.name for f in result.schema.fields}
    assert names == {"id", "name", "email", "age"}


def test_blend_disjoint_no_conflicts():
    left = _schema(_field("id"))
    right = _schema(_field("email"))
    result = blend_schemas(left, right)
    assert bool(result) is True
    assert result.conflicts == []


def test_blend_identical_fields_no_conflict():
    f = _field("id", FieldType.STRING)
    left = _schema(f)
    right = _schema(_field("id", FieldType.STRING))
    result = blend_schemas(left, right)
    assert len(result.conflicts) == 0
    assert len(result.schema.fields) == 1


def test_blend_type_conflict_default_favours_left():
    left = _schema(_field("count", FieldType.INTEGER))
    right = _schema(_field("count", FieldType.STRING))
    result = blend_schemas(left, right)
    assert len(result.conflicts) == 1
    conflict = result.conflicts[0]
    assert conflict.field_name == "count"
    assert conflict.chosen == "left"
    assert result.schema.fields[0].field_type == FieldType.INTEGER


def test_blend_type_conflict_higher_right_weight_favours_right():
    left = _schema(_field("count", FieldType.INTEGER))
    right = _schema(_field("count", FieldType.STRING))
    result = blend_schemas(left, right, left_weight=1.0, right_weight=2.0)
    assert result.conflicts[0].chosen == "right"
    assert result.schema.fields[0].field_type == FieldType.STRING


def test_blend_required_wins_over_optional_same_type():
    left = _schema(_field("val", FieldType.STRING, required=False))
    right = _schema(_field("val", FieldType.STRING, required=True))
    result = blend_schemas(left, right)
    assert result.schema.fields[0].required is True
    assert len(result.conflicts) == 0


def test_blend_result_bool_false_when_conflicts():
    left = _schema(_field("x", FieldType.INTEGER))
    right = _schema(_field("x", FieldType.STRING))
    result = blend_schemas(left, right)
    assert bool(result) is False


def test_blend_result_to_dict_structure():
    left = _schema(_field("id"))
    right = _schema(_field("id", FieldType.INTEGER))
    result = blend_schemas(left, right)
    d = result.to_dict()
    assert "fields" in d
    assert "conflict_count" in d
    assert "conflicts" in d
    assert d["conflict_count"] == 1


def test_blend_conflict_to_dict():
    c = BlendConflict(field_name="x", left_type="string", right_type="integer", chosen="left")
    d = c.to_dict()
    assert d["field"] == "x"
    assert d["chosen"] == "left"


def test_blend_str_representation():
    left = _schema(_field("a", FieldType.INTEGER))
    right = _schema(_field("a", FieldType.STRING))
    result = blend_schemas(left, right)
    text = str(result)
    assert "BlendResult" in text
    assert "conflict" in text
