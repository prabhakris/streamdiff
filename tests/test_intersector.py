"""Tests for streamdiff.intersector."""
import pytest

from streamdiff.schema import SchemaField, FieldType, StreamSchema
from streamdiff.intersector import intersect_schemas, IntersectResult


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(fields=list(fields))


# ---------------------------------------------------------------------------
# Basic correctness
# ---------------------------------------------------------------------------

def test_disjoint_schemas_no_common():
    left = _schema(_field("a"), _field("b"))
    right = _schema(_field("c"), _field("d"))
    result = intersect_schemas(left, right)
    assert result.common == []
    assert len(result.only_left) == 2
    assert len(result.only_right) == 2


def test_identical_schemas_all_common():
    left = _schema(_field("x"), _field("y"))
    right = _schema(_field("x"), _field("y"))
    result = intersect_schemas(left, right)
    assert {f.name for f in result.common} == {"x", "y"}
    assert result.only_left == []
    assert result.only_right == []


def test_partial_overlap():
    left = _schema(_field("a"), _field("b"), _field("c"))
    right = _schema(_field("b"), _field("c"), _field("d"))
    result = intersect_schemas(left, right)
    assert {f.name for f in result.common} == {"b", "c"}
    assert [f.name for f in result.only_left] == ["a"]
    assert [f.name for f in result.only_right] == ["d"]


def test_common_uses_left_field_definition():
    """When a field appears in both, the left definition is kept."""
    lf = SchemaField(name="score", field_type=FieldType.INT, required=True)
    rf = SchemaField(name="score", field_type=FieldType.FLOAT, required=False)
    result = intersect_schemas(_schema(lf), _schema(rf))
    assert len(result.common) == 1
    assert result.common[0].field_type == FieldType.INT
    assert result.common[0].required is True


def test_empty_left_schema():
    left = _schema()
    right = _schema(_field("a"))
    result = intersect_schemas(left, right)
    assert result.common == []
    assert result.only_left == []
    assert result.only_right == [_field("a")]


def test_empty_right_schema():
    left = _schema(_field("a"))
    right = _schema()
    result = intersect_schemas(left, right)
    assert result.common == []
    assert result.only_left == [_field("a")]
    assert result.only_right == []


def test_both_empty_schemas():
    result = intersect_schemas(_schema(), _schema())
    assert result.common == []
    assert result.only_left == []
    assert result.only_right == []


# ---------------------------------------------------------------------------
# Bool / helpers
# ---------------------------------------------------------------------------

def test_bool_true_when_common_fields():
    left = _schema(_field("a"))
    right = _schema(_field("a"))
    assert bool(intersect_schemas(left, right)) is True


def test_bool_false_when_no_common_fields():
    left = _schema(_field("a"))
    right = _schema(_field("b"))
    assert bool(intersect_schemas(left, right)) is False


def test_to_schema_contains_only_common():
    left = _schema(_field("a"), _field("b"))
    right = _schema(_field("b"), _field("c"))
    result = intersect_schemas(left, right)
    schema = result.to_schema()
    assert [f.name for f in schema.fields] == ["b"]


def test_to_dict_keys():
    left = _schema(_field("a"), _field("b"))
    right = _schema(_field("b"), _field("c"))
    d = intersect_schemas(left, right).to_dict()
    assert set(d.keys()) == {
        "common", "only_left", "only_right",
        "common_count", "only_left_count", "only_right_count",
    }
    assert d["common_count"] == 1
    assert d["only_left_count"] == 1
    assert d["only_right_count"] == 1


def test_str_representation():
    left = _schema(_field("a"))
    right = _schema(_field("a"), _field("b"))
    s = str(intersect_schemas(left, right))
    assert "common=1" in s
    assert "only_left=0" in s
    assert "only_right=1" in s
