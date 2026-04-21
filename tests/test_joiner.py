"""Tests for streamdiff.joiner."""
import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.joiner import join_schemas, JoinConflict, JoinResult


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, type=ftype, required=required)


def _schema(name: str, fields) -> StreamSchema:
    return StreamSchema(name=name, fields=list(fields))


def test_join_disjoint_schemas_combines_all_fields():
    left = _schema("L", [_field("a"), _field("b")])
    right = _schema("R", [_field("c"), _field("d")])
    result = join_schemas(left, right)
    names = [f.name for f in result.schema.fields]
    assert "a" in names
    assert "b" in names
    assert "c" in names
    assert "d" in names
    assert result.conflicts == []
    assert result.left_only == ["a", "b"]
    assert result.right_only == ["c", "d"]


def test_join_identical_fields_no_conflict():
    left = _schema("L", [_field("x")])
    right = _schema("R", [_field("x")])
    result = join_schemas(left, right)
    assert result.conflicts == []
    assert len(result.schema.fields) == 1
    assert result.left_only == []
    assert result.right_only == []


def test_join_type_conflict_detected():
    left = _schema("L", [_field("val", FieldType.STRING)])
    right = _schema("R", [_field("val", FieldType.INT)])
    result = join_schemas(left, right)
    assert len(result.conflicts) == 1
    c = result.conflicts[0]
    assert c.field_name == "val"
    assert c.left_type == FieldType.STRING.value
    assert c.right_type == FieldType.INT.value


def test_join_prefer_left_on_conflict():
    left = _schema("L", [_field("val", FieldType.STRING)])
    right = _schema("R", [_field("val", FieldType.INT)])
    result = join_schemas(left, right, prefer="left")
    merged_field = next(f for f in result.schema.fields if f.name == "val")
    assert merged_field.type == FieldType.STRING


def test_join_prefer_right_on_conflict():
    left = _schema("L", [_field("val", FieldType.STRING)])
    right = _schema("R", [_field("val", FieldType.INT)])
    result = join_schemas(left, right, prefer="right")
    merged_field = next(f for f in result.schema.fields if f.name == "val")
    assert merged_field.type == FieldType.INT


def test_join_result_bool_true_when_no_conflicts():
    left = _schema("L", [_field("a")])
    right = _schema("R", [_field("b")])
    result = join_schemas(left, right)
    assert bool(result) is True


def test_join_result_bool_false_when_conflicts():
    left = _schema("L", [_field("x", FieldType.STRING)])
    right = _schema("R", [_field("x", FieldType.BOOLEAN)])
    result = join_schemas(left, right)
    assert bool(result) is False


def test_join_conflict_to_dict():
    c = JoinConflict(field_name="f", left_type="string", right_type="int")
    d = c.to_dict()
    assert d["field"] == "f"
    assert d["left_type"] == "string"
    assert d["right_type"] == "int"


def test_join_result_to_dict_keys():
    left = _schema("L", [_field("a")])
    right = _schema("R", [_field("b")])
    result = join_schemas(left, right)
    d = result.to_dict()
    assert "fields" in d
    assert "conflicts" in d
    assert "left_only" in d
    assert "right_only" in d


def test_join_result_str_contains_field_count():
    left = _schema("L", [_field("a"), _field("b")])
    right = _schema("R", [_field("c")])
    result = join_schemas(left, right)
    assert "3" in str(result)


def test_join_conflict_str():
    c = JoinConflict(field_name="score", left_type="int", right_type="float")
    s = str(c)
    assert "score" in s
    assert "int" in s
    assert "float" in s
