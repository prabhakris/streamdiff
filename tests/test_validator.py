"""Tests for streamdiff.validator."""
import pytest

from streamdiff.schema import SchemaField, FieldType
from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.validator import validate, is_valid, ValidationIssue


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = False) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _result(*changes: SchemaChange) -> DiffResult:
    return DiffResult(changes=list(changes))


def test_no_issues_when_no_changes():
    result = _result()
    assert is_valid(result)
    assert validate(result) == []


def test_added_optional_field_is_valid():
    change = SchemaChange(
        field_name="new_field",
        change_type=ChangeType.ADDED,
        old_field=None,
        new_field=_field("new_field", required=False),
    )
    assert is_valid(_result(change))


def test_added_required_field_is_invalid():
    change = SchemaChange(
        field_name="req_field",
        change_type=ChangeType.ADDED,
        old_field=None,
        new_field=_field("req_field", required=True),
    )
    issues = validate(_result(change))
    assert len(issues) == 1
    assert issues[0].rule == "NO_REQUIRED_ADD"
    assert "req_field" in issues[0].message


def test_removed_field_is_invalid():
    change = SchemaChange(
        field_name="old_field",
        change_type=ChangeType.REMOVED,
        old_field=_field("old_field"),
        new_field=None,
    )
    issues = validate(_result(change))
    assert any(i.rule == "NO_REMOVAL" for i in issues)


def test_type_change_is_invalid():
    change = SchemaChange(
        field_name="amount",
        change_type=ChangeType.TYPE_CHANGED,
        old_field=_field("amount", FieldType.INTEGER),
        new_field=_field("amount", FieldType.STRING),
    )
    issues = validate(_result(change))
    assert len(issues) == 1
    assert issues[0].rule == "NO_TYPE_CHANGE"
    assert "integer" in issues[0].message.lower() or "string" in issues[0].message.lower()


def test_issue_str_representation():
    change = SchemaChange(
        field_name="x",
        change_type=ChangeType.REMOVED,
        old_field=_field("x"),
        new_field=None,
    )
    issue = validate(_result(change))[0]
    text = str(issue)
    assert "NO_REMOVAL" in text
    assert "x" in text


def test_multiple_issues_in_one_result():
    changes = [
        SchemaChange(field_name="a", change_type=ChangeType.REMOVED, old_field=_field("a"), new_field=None),
        SchemaChange(field_name="b", change_type=ChangeType.ADDED, old_field=None, new_field=_field("b", required=True)),
    ]
    issues = validate(_result(*changes))
    assert len(issues) == 2
