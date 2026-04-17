"""Tests for streamdiff.linter."""
import pytest

from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.linter import lint_schema, has_errors, LintIssue


def _field(name: str, required: bool = False) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _schema(*field_names: str) -> StreamSchema:
    fields = [_field(n) for n in field_names]
    return StreamSchema(name="test", fields=fields)


def test_clean_schema_has_no_issues():
    schema = _schema("user_id", "event_name", "created_at")
    issues = lint_schema(schema)
    assert issues == []


def test_camel_case_name_triggers_warning():
    schema = _schema("userId")
    issues = lint_schema(schema)
    assert len(issues) == 1
    assert "snake_case" in issues[0].message
    assert issues[0].field_name == "userId"


def test_uppercase_name_triggers_warning():
    schema = _schema("UserID")
    issues = lint_schema(schema)
    assert any("snake_case" in i.message for i in issues)


def test_name_with_hyphen_triggers_warning():
    schema = _schema("user-id")
    issues = lint_schema(schema)
    assert any("snake_case" in i.message for i in issues)


def test_name_too_long_triggers_warning():
    long_name = "a" * 65
    schema = _schema(long_name)
    issues = lint_schema(schema)
    assert any("maximum length" in i.message for i in issues)


def test_name_at_max_length_is_ok():
    name = "a" * 64
    schema = _schema(name)
    issues = lint_schema(schema)
    # only possible issue is snake_case (all lowercase letters — passes)
    assert not any("maximum length" in i.message for i in issues)


def test_reserved_word_triggers_warning():
    schema = _schema("timestamp")
    issues = lint_schema(schema)
    assert any("reserved" in i.message for i in issues)
    assert issues[0].severity == "warning"


def test_has_errors_false_for_warnings_only():
    schema = _schema("timestamp")
    issues = lint_schema(schema)
    assert not has_errors(issues)


def test_has_errors_true_when_error_present():
    issues = [LintIssue(field_name="", message="empty", severity="error")]
    assert has_errors(issues)


def test_multiple_fields_accumulate_issues():
    schema = _schema("goodField", "timestamp", "ok_field")
    issues = lint_schema(schema)
    field_names = [i.field_name for i in issues]
    assert "goodField" in field_names
    assert "timestamp" in field_names
    assert "ok_field" not in field_names


def test_lint_issue_str():
    issue = LintIssue(field_name="foo", message="bad name", severity="warning")
    assert str(issue) == "[WARNING] foo: bad name"
