"""Tests for streamdiff.masker."""
import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.masker import mask_schema, MaskResult, _is_sensitive, _mask_name


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test_stream", fields=list(fields))


# --- unit helpers ---

def test_is_sensitive_password():
    assert _is_sensitive("password") is True


def test_is_sensitive_token_mixed_case():
    assert _is_sensitive("authToken") is True


def test_is_sensitive_safe_field():
    assert _is_sensitive("user_id") is False


def test_mask_name_long_name():
    result = _mask_name("password", "***")
    assert result.startswith("***_")
    assert result.endswith("ord")


def test_mask_name_short_name():
    result = _mask_name("pw", "***")
    assert result == "***"


# --- mask_schema ---

def test_no_sensitive_fields_returns_all():
    s = _schema(_field("user_id"), _field("email"))
    result = mask_schema(s)
    assert not result
    assert len(result.schema.fields) == 2
    assert result.masked == []


def test_password_field_is_masked():
    s = _schema(_field("user_id"), _field("password"))
    result = mask_schema(s)
    assert bool(result) is True
    assert len(result.masked) == 1
    assert result.masked[0].original_name == "password"


def test_token_field_is_masked():
    s = _schema(_field("auth_token"), _field("name"))
    result = mask_schema(s)
    assert len(result.masked) == 1
    assert result.masked[0].original_name == "auth_token"


def test_masked_field_replaced_in_schema():
    s = _schema(_field("secret_key"), _field("region"))
    result = mask_schema(s)
    names = [f.name for f in result.schema.fields]
    assert "secret_key" not in names
    assert "region" in names


def test_original_count_preserved():
    s = _schema(_field("password"), _field("user"), _field("token"))
    result = mask_schema(s)
    assert result.original_count == 3


def test_extra_patterns_applied():
    s = _schema(_field("api_code"), _field("name"))
    result = mask_schema(s, extra_patterns=["code"])
    assert len(result.masked) == 1
    assert result.masked[0].original_name == "api_code"


def test_to_dict_structure():
    s = _schema(_field("password"), _field("user_id"))
    result = mask_schema(s)
    d = result.to_dict()
    assert d["stream"] == "test_stream"
    assert d["masked_count"] == 1
    assert d["original_count"] == 2
    assert isinstance(d["masked_fields"], list)


def test_str_no_masked():
    s = _schema(_field("name"))
    result = mask_schema(s)
    assert "No fields masked" in str(result)


def test_str_with_masked():
    s = _schema(_field("password"))
    result = mask_schema(s)
    assert "Masked" in str(result)
    assert "->" in str(result)
