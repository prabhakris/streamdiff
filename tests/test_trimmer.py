import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.trimmer import trim_by_types, trim_by_pattern, trim_optional, TrimResult


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_trim_by_types_removes_matching():
    schema = _schema(_field("a", FieldType.STRING), _field("b", FieldType.INT), _field("c", FieldType.STRING))
    result = trim_by_types(schema, {"string"})
    assert len(result.trimmed) == 2
    assert result.schema.field_map["b"] is not None
    assert "a" not in result.schema.field_map


def test_trim_by_types_no_match_keeps_all():
    schema = _schema(_field("x", FieldType.INT), _field("y", FieldType.LONG))
    result = trim_by_types(schema, {"string"})
    assert not result
    assert len(result.schema.fields) == 2


def test_trim_by_types_original_count():
    schema = _schema(_field("a"), _field("b"), _field("c"))
    result = trim_by_types(schema, {"string"})
    assert result.original_count == 3


def test_trim_by_pattern_removes_matching():
    schema = _schema(_field("user_id"), _field("user_name"), _field("email"))
    result = trim_by_pattern(schema, "user")
    assert len(result.trimmed) == 2
    assert result.schema.fields[0].name == "email"


def test_trim_by_pattern_case_insensitive():
    schema = _schema(_field("UserID"), _field("score"))
    result = trim_by_pattern(schema, "user")
    assert len(result.trimmed) == 1
    assert result.trimmed[0].name == "UserID"


def test_trim_by_pattern_no_match():
    schema = _schema(_field("alpha"), _field("beta"))
    result = trim_by_pattern(schema, "gamma")
    assert not result
    assert len(result.schema.fields) == 2


def test_trim_optional_removes_optional_fields():
    schema = _schema(
        _field("req", required=True),
        _field("opt", required=False),
        _field("opt2", required=False),
    )
    result = trim_optional(schema)
    assert len(result.trimmed) == 2
    assert all(f.required for f in result.schema.fields)


def test_trim_optional_all_required_no_change():
    schema = _schema(_field("a", required=True), _field("b", required=True))
    result = trim_optional(schema)
    assert not result
    assert len(result.schema.fields) == 2


def test_to_dict_structure():
    schema = _schema(_field("a"), _field("b", required=False))
    result = trim_optional(schema)
    d = result.to_dict()
    assert d["original_count"] == 2
    assert d["trimmed_count"] == 1
    assert "b" in d["trimmed_fields"]
    assert d["remaining_count"] == 1


def test_str_no_trimmed():
    schema = _schema(_field("a", required=True))
    result = trim_optional(schema)
    assert str(result) == "No fields trimmed."


def test_str_with_trimmed():
    schema = _schema(_field("x", required=False))
    result = trim_optional(schema)
    assert "x" in str(result)
    assert "1" in str(result)
