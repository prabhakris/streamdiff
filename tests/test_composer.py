"""Tests for streamdiff.composer."""
import pytest

from streamdiff.schema import FieldType, SchemaField, StreamSchema
from streamdiff.composer import ComposeConflict, ComposeResult, compose_schemas


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(name: str, fields) -> StreamSchema:
    return StreamSchema(name=name, fields=fields)


# ---------------------------------------------------------------------------
# compose_schemas — happy paths
# ---------------------------------------------------------------------------

def test_compose_disjoint_schemas_combines_all_fields():
    a = _schema("A", [_field("id"), _field("name")])
    b = _schema("B", [_field("age", FieldType.INTEGER)])
    result = compose_schemas([("A", a), ("B", b)])
    assert bool(result) is True
    assert result.schema is not None
    names = {f.name for f in result.schema.fields}
    assert names == {"id", "name", "age"}


def test_compose_identical_fields_no_conflict():
    a = _schema("A", [_field("id")])
    b = _schema("B", [_field("id")])
    result = compose_schemas([("A", a), ("B", b)])
    assert bool(result) is True
    assert len(result.conflicts) == 0
    assert len(result.schema.fields) == 1


def test_compose_required_union_makes_field_required():
    a = _schema("A", [_field("x", required=False)])
    b = _schema("B", [_field("x", required=True)])
    result = compose_schemas([("A", a), ("B", b)])
    assert bool(result) is True
    composed_field = result.schema.fields[0]
    assert composed_field.required is True


def test_compose_source_names_recorded():
    a = _schema("alpha", [_field("a")])
    b = _schema("beta", [_field("b")])
    result = compose_schemas([("alpha", a), ("beta", b)])
    assert result.source_names == ["alpha", "beta"]


# ---------------------------------------------------------------------------
# conflict handling
# ---------------------------------------------------------------------------

def test_compose_type_conflict_detected():
    a = _schema("A", [_field("val", FieldType.STRING)])
    b = _schema("B", [_field("val", FieldType.INTEGER)])
    result = compose_schemas([("A", a), ("B", b)], on_conflict="fail")
    assert bool(result) is False
    assert len(result.conflicts) == 1
    assert result.conflicts[0].field_name == "val"
    assert result.schema is None


def test_compose_on_conflict_first_keeps_first_type():
    a = _schema("A", [_field("val", FieldType.STRING)])
    b = _schema("B", [_field("val", FieldType.INTEGER)])
    result = compose_schemas([("A", a), ("B", b)], on_conflict="first")
    assert result.schema is not None
    composed_field = result.schema.fields[0]
    assert composed_field.field_type == FieldType.STRING


def test_compose_on_conflict_last_keeps_last_type():
    a = _schema("A", [_field("val", FieldType.STRING)])
    b = _schema("B", [_field("val", FieldType.INTEGER)])
    result = compose_schemas([("A", a), ("B", b)], on_conflict="last")
    assert result.schema is not None
    composed_field = result.schema.fields[0]
    assert composed_field.field_type == FieldType.INTEGER


# ---------------------------------------------------------------------------
# to_dict / __str__
# ---------------------------------------------------------------------------

def test_compose_result_to_dict_ok():
    a = _schema("A", [_field("id")])
    result = compose_schemas([("A", a)])
    d = result.to_dict()
    assert d["ok"] is True
    assert d["sources"] == ["A"]
    assert len(d["fields"]) == 1
    assert d["conflicts"] == []


def test_conflict_str_contains_field_name():
    c = ComposeConflict(field_name="val", sources=["A", "B"], reason="type mismatch: string vs integer")
    assert "val" in str(c)
    assert "A" in str(c)
    assert "B" in str(c)


def test_conflict_to_dict_keys():
    c = ComposeConflict(field_name="x", sources=["s1", "s2"], reason="test")
    d = c.to_dict()
    assert set(d.keys()) == {"field", "sources", "reason"}
