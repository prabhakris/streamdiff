import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.indexer import build_index, FieldIndex, IndexEntry


def _field(name: str, ft: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ft, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_empty_schema_returns_empty_index():
    idx = build_index(_schema())
    assert len(idx) == 0


def test_single_field_indexed():
    idx = build_index(_schema(_field("user_id")))
    assert "user_id" in idx.entries


def test_entry_attributes():
    idx = build_index(_schema(_field("age", FieldType.INT, required=False)))
    e = idx.get("age")
    assert e is not None
    assert e.field_type == FieldType.INT
    assert e.required is False
    assert e.depth == 0


def test_depth_nested_name():
    idx = build_index(_schema(_field("user.address.city")))
    e = idx.get("user.address.city")
    assert e.depth == 2


def test_search_by_substring():
    idx = build_index(_schema(_field("user_id"), _field("user_name"), _field("age")))
    results = idx.search("user")
    names = {r.name for r in results}
    assert names == {"user_id", "user_name"}


def test_search_case_insensitive():
    idx = build_index(_schema(_field("UserID")))
    assert idx.search("userid")


def test_by_type_filters_correctly():
    idx = build_index(_schema(
        _field("a", FieldType.STRING),
        _field("b", FieldType.INT),
        _field("c", FieldType.STRING),
    ))
    strings = idx.by_type(FieldType.STRING)
    assert len(strings) == 2


def test_required_and_optional_split():
    idx = build_index(_schema(
        _field("x", required=True),
        _field("y", required=False),
    ))
    assert len(idx.required_fields()) == 1
    assert len(idx.optional_fields()) == 1


def test_to_dict_keys():
    idx = build_index(_schema(_field("ts", FieldType.STRING)))
    d = idx.get("ts").to_dict()
    assert set(d.keys()) == {"name", "type", "required", "depth"}


def test_str_representation():
    e = IndexEntry(name="id", field_type=FieldType.STRING, required=True, depth=0)
    assert "id" in str(e)
    assert "required" in str(e)
