import pytest
from streamdiff.diff import diff_schemas, ChangeType
from streamdiff.schema import StreamSchema, SchemaField, FieldType


def make_schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", version="1.0", fields=list(fields))


def field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True, nullable: bool = False) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required, nullable=nullable)


def test_no_changes():
    schema = make_schema(field("id"), field("name"))
    result = diff_schemas(schema, schema)
    assert result.changes == []
    assert not result.has_breaking_changes


def test_added_optional_field():
    old = make_schema(field("id"))
    new = make_schema(field("id"), field("tag", required=False))
    result = diff_schemas(old, new)
    assert len(result.changes) == 1
    assert result.changes[0].change_type == ChangeType.ADDED_OPTIONAL
    assert not result.has_breaking_changes


def test_added_required_field_is_breaking():
    old = make_schema(field("id"))
    new = make_schema(field("id"), field("email", required=True))
    result = diff_schemas(old, new)
    assert result.has_breaking_changes
    assert result.breaking_changes[0].change_type == ChangeType.ADDED_REQUIRED


def test_removed_field_is_breaking():
    old = make_schema(field("id"), field("name"))
    new = make_schema(field("id"))
    result = diff_schemas(old, new)
    assert result.has_breaking_changes
    assert result.breaking_changes[0].change_type == ChangeType.REMOVED


def test_type_change_is_breaking():
    old = make_schema(field("id", FieldType.STRING))
    new = make_schema(field("id", FieldType.INTEGER))
    result = diff_schemas(old, new)
    assert result.has_breaking_changes
    assert result.breaking_changes[0].change_type == ChangeType.TYPE_CHANGED


def test_nullability_change_is_non_breaking():
    old = make_schema(field("id", nullable=False))
    new = make_schema(field("id", nullable=True))
    result = diff_schemas(old, new)
    assert len(result.changes) == 1
    assert result.changes[0].change_type == ChangeType.NULLABILITY_CHANGED
    assert not result.has_breaking_changes


def test_breaking_and_non_breaking_mixed():
    old = make_schema(field("id"), field("name"))
    new = make_schema(field("id"), field("tag", required=False))
    result = diff_schemas(old, new)
    assert len(result.breaking_changes) == 1
    assert len(result.non_breaking_changes) == 1
