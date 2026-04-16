"""Tests for schema diffing logic."""

import pytest

from streamdiff.schema import (
    FieldType,
    SchemaField,
    SchemaDiff,
    StreamSchema,
    diff_schemas,
)


def make_schema(fields: list[SchemaField], version: str = "1.0.0") -> StreamSchema:
    return StreamSchema(name="test-stream", version=version, fields=fields)


USER_ID = SchemaField(name="user_id", type=FieldType.STRING)
EMAIL = SchemaField(name="email", type=FieldType.STRING)
AGE = SchemaField(name="age", type=FieldType.INTEGER, required=False)


def test_no_changes():
    old = make_schema([USER_ID, EMAIL])
    new = make_schema([USER_ID, EMAIL])
    result = diff_schemas(old, new)
    assert not result.has_changes
    assert not result.is_breaking


def test_added_optional_field():
    old = make_schema([USER_ID])
    new = make_schema([USER_ID, AGE])
    result = diff_schemas(old, new)
    assert len(result.added) == 1
    assert result.added[0].name == "age"
    assert not result.is_breaking


def test_added_required_field_is_breaking():
    old = make_schema([USER_ID])
    new = make_schema([USER_ID, EMAIL])  # EMAIL is required by default
    result = diff_schemas(old, new)
    assert result.is_breaking


def test_removed_field_is_breaking():
    old = make_schema([USER_ID, EMAIL])
    new = make_schema([USER_ID])
    result = diff_schemas(old, new)
    assert len(result.removed) == 1
    assert result.is_breaking


def test_type_change_is_breaking():
    old_age = SchemaField(name="age", type=FieldType.STRING)
    new_age = SchemaField(name="age", type=FieldType.INTEGER)
    old = make_schema([USER_ID, old_age])
    new = make_schema([USER_ID, new_age])
    result = diff_schemas(old, new)
    assert len(result.modified) == 1
    assert result.is_breaking


def test_nullable_change_not_breaking():
    old_field = SchemaField(name="email", type=FieldType.STRING, nullable=False)
    new_field = SchemaField(name="email", type=FieldType.STRING, nullable=True)
    old = make_schema([USER_ID, old_field])
    new = make_schema([USER_ID, new_field])
    result = diff_schemas(old, new)
    assert len(result.modified) == 1
    assert not result.is_breaking
