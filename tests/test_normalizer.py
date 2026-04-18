import pytest
from streamdiff.schema import SchemaField, FieldType, StreamSchema
from streamdiff.normalizer import (
    NormalizeConfig,
    normalize_field,
    normalize_schema,
    _snake_to_camel,
    _camel_to_snake,
    _lowercase,
)


def _field(name: str) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=True, nullable=False)


def _schema(*names: str) -> StreamSchema:
    return StreamSchema(name="test", fields=[_field(n) for n in names])


def test_snake_to_camel_simple():
    assert _snake_to_camel("user_id") == "userId"


def test_snake_to_camel_multiple():
    assert _snake_to_camel("created_at_time") == "createdAtTime"


def test_snake_to_camel_no_underscore():
    assert _snake_to_camel("name") == "name"


def test_camel_to_snake_simple():
    assert _camel_to_snake("userId") == "user_id"


def test_camel_to_snake_acronym():
    assert _camel_to_snake("userIDValue") == "user_id_value"


def test_lowercase():
    assert _lowercase("UserID") == "userid"


def test_normalize_field_renames():
    f = _field("user_id")
    config = NormalizeConfig(strategy="snake_to_camel")
    result = normalize_field(f, config.get_fn())
    assert result.name == "userId"
    assert result.field_type == FieldType.STRING
    assert result.required is True


def test_normalize_schema_renames_all_fields():
    schema = _schema("user_id", "created_at", "event_type")
    config = NormalizeConfig(strategy="snake_to_camel")
    result = normalize_schema(schema, config)
    assert [f.name for f in result.fields] == ["userId", "createdAt", "eventType"]


def test_normalize_schema_preserves_stream_name():
    schema = _schema("field_one")
    config = NormalizeConfig(strategy="lowercase")
    result = normalize_schema(schema, config)
    assert result.name == "test"


def test_normalize_none_strategy_is_identity():
    schema = _schema("myField", "anotherField")
    config = NormalizeConfig(strategy="none")
    result = normalize_schema(schema, config)
    assert [f.name for f in result.fields] == ["myField", "anotherField"]


def test_unknown_strategy_raises():
    config = NormalizeConfig(strategy="invalid")
    with pytest.raises(ValueError, match="Unknown normalization strategy"):
        config.get_fn()
