import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.redactor import (
    redact_schema,
    redact_all,
    RedactResult,
    SENSITIVE_PATTERNS,
)


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _schema(*names: str) -> StreamSchema:
    return StreamSchema(name="test", fields=[_field(n) for n in names])


def test_no_sensitive_fields_returns_all():
    s = _schema("user_id", "email", "created_at")
    result = redact_schema(s)
    assert len(result.schema.fields) == 3
    assert result.redacted_fields == []
    assert not result


def test_password_field_is_redacted():
    s = _schema("user_id", "password", "email")
    result = redact_schema(s)
    assert "password" in result.redacted_fields
    assert len(result.schema.fields) == 2
    assert result


def test_token_field_is_redacted():
    s = _schema("access_token", "name")
    result = redact_schema(s)
    assert "access_token" in result.redacted_fields


def test_secret_key_is_redacted():
    s = _schema("api_secret", "api_key", "endpoint")
    result = redact_schema(s)
    assert set(result.redacted_fields) == {"api_secret", "api_key"}
    assert len(result.schema.fields) == 1


def test_custom_patterns():
    s = _schema("internal_id", "public_id", "name")
    result = redact_schema(s, patterns=["internal"])
    assert result.redacted_fields == ["internal_id"]
    assert len(result.schema.fields) == 2


def test_original_count_preserved():
    s = _schema("a", "b", "password", "c")
    result = redact_schema(s)
    assert result.original_count == 4


def test_to_dict_contains_counts():
    s = _schema("password", "name")
    d = redact_schema(s).to_dict()
    assert d["original_count"] == 2
    assert d["redacted_count"] == 1
    assert d["redacted_fields"] == ["password"]


def test_redact_all_applies_to_each_schema():
    s1 = _schema("password", "user")
    s2 = _schema("token", "id")
    results = redact_all([s1, s2])
    assert len(results) == 2
    assert results[0].redacted_fields == ["password"]
    assert results[1].redacted_fields == ["token"]


def test_schema_name_preserved():
    s = StreamSchema(name="my_stream", fields=[_field("password")])
    result = redact_schema(s)
    assert result.schema.name == "my_stream"
