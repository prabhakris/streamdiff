import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.sorter import sort_fields, SortResult


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_sort_by_name_ascending():
    schema = _schema(_field("zebra"), _field("apple"), _field("mango"))
    result = sort_fields(schema, key="name")
    assert [f.name for f in result.fields] == ["apple", "mango", "zebra"]
    assert result.key == "name"


def test_sort_by_name_descending():
    schema = _schema(_field("zebra"), _field("apple"), _field("mango"))
    result = sort_fields(schema, key="name", reverse=True)
    assert [f.name for f in result.fields] == ["zebra", "mango", "apple"]


def test_sort_by_type():
    schema = _schema(
        _field("a", FieldType.STRING),
        _field("b", FieldType.INT),
        _field("c", FieldType.BOOLEAN),
    )
    result = sort_fields(schema, key="type")
    types = [f.field_type.value for f in result.fields]
    assert types == sorted(types)


def test_sort_by_required_puts_required_first():
    schema = _schema(
        _field("opt", required=False),
        _field("req", required=True),
        _field("opt2", required=False),
    )
    result = sort_fields(schema, key="required")
    assert result.fields[0].required is True
    assert all(not f.required for f in result.fields[1:])


def test_sort_invalid_key_raises():
    schema = _schema(_field("x"))
    with pytest.raises(ValueError, match="Unsupported sort key"):
        sort_fields(schema, key="unknown")


def test_sort_result_schema_name():
    schema = _schema(_field("a"))
    result = sort_fields(schema, key="name")
    assert result.schema_name == "test"


def test_sort_result_to_dict():
    schema = _schema(_field("b"), _field("a"))
    result = sort_fields(schema, key="name")
    d = result.to_dict()
    assert d["key"] == "name"
    assert d["fields"][0]["name"] == "a"
    assert d["fields"][1]["name"] == "b"


def test_sort_result_str():
    schema = _schema(_field("z"), _field("a"))
    result = sort_fields(schema, key="name")
    text = str(result)
    assert "sorted by name" in text
    assert "a" in text
