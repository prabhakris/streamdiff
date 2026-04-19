import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.cloner import clone_schema, CloneResult


def _field(name: str, ft: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ft, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_clone_empty_schema():
    s = _schema()
    result = clone_schema(s)
    assert isinstance(result, CloneResult)
    assert len(result.cloned.fields) == 0
    assert result.remapped == {}


def test_clone_preserves_fields():
    s = _schema(_field("id"), _field("name"))
    result = clone_schema(s)
    names = [f.name for f in result.cloned.fields]
    assert names == ["id", "name"]


def test_clone_is_independent_copy():
    s = _schema(_field("id"))
    result = clone_schema(s)
    result.cloned.fields[0] = _field("other")
    assert s.fields[0].name == "id"


def test_clone_with_type_map():
    s = _schema(_field("count", FieldType.INT))
    result = clone_schema(s, type_map={"count": FieldType.LONG})
    assert result.cloned.fields[0].field_type == FieldType.LONG
    assert "count" in result.remapped
    assert result.remapped["count"] == FieldType.LONG


def test_clone_type_map_no_match_leaves_type():
    s = _schema(_field("val", FieldType.STRING))
    result = clone_schema(s, type_map={"other": FieldType.INT})
    assert result.cloned.fields[0].field_type == FieldType.STRING
    assert result.remapped == {}


def test_clone_with_name_fn():
    s = _schema(_field("user_id"), _field("user_name"))
    result = clone_schema(s, name_fn=lambda n: n.upper())
    names = [f.name for f in result.cloned.fields]
    assert names == ["USER_ID", "USER_NAME"]


def test_clone_bool_is_true():
    s = _schema(_field("x"))
    assert bool(clone_schema(s))


def test_clone_to_dict():
    s = _schema(_field("a"), _field("b"))
    d = clone_schema(s).to_dict()
    assert d["original_fields"] == 2
    assert d["cloned_fields"] == 2
    assert d["remapped"] == {}


def test_clone_str_no_remaps():
    s = _schema(_field("x"))
    out = str(clone_schema(s))
    assert "1 field" in out


def test_clone_str_with_remaps():
    s = _schema(_field("n", FieldType.INT))
    out = str(clone_schema(s, type_map={"n": FieldType.DOUBLE}))
    assert "remapped" in out
    assert "n" in out
