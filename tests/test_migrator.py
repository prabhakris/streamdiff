import pytest
from streamdiff.diff import SchemaChange, ChangeType, DiffResult
from streamdiff.schema import SchemaField, FieldType
from streamdiff.migrator import (
    MigrationHint,
    build_hints,
    format_hints_text,
    format_hints_dict,
    _hint_for,
)


def _field(name="f", ftype=FieldType.STRING, required=False):
    return SchemaField(name=name, field_type=ftype, required=required)


def _change(name, ct, old=None, new=None):
    return SchemaChange(field_name=name, change_type=ct, old_field=old, new_field=new)


def _result(changes):
    return DiffResult(changes=changes)


def test_no_changes_returns_empty_hints():
    result = _result([])
    hints = build_hints(result)
    assert hints == []


def test_added_optional_hint():
    f = _field("score", required=False)
    c = _change("score", ChangeType.ADDED, new=f)
    hint = _hint_for(c)
    assert "optional" in hint.hint
    assert hint.example != ""


def test_added_required_hint():
    f = _field("user_id", required=True)
    c = _change("user_id", ChangeType.ADDED, new=f)
    hint = _hint_for(c)
    assert "required" in hint.hint
    assert "producers" in hint.hint


def test_removed_hint():
    f = _field("legacy")
    c = _change("legacy", ChangeType.REMOVED, old=f)
    hint = _hint_for(c)
    assert "consumers" in hint.hint
    assert "legacy" in hint.hint


def test_type_changed_hint():
    old = _field("count", FieldType.INT)
    new = _field("count", FieldType.LONG)
    c = _change("count", ChangeType.TYPE_CHANGED, old=old, new=new)
    hint = _hint_for(c)
    assert "int" in hint.hint
    assert "long" in hint.hint


def test_build_hints_multiple():
    changes = [
        _change("a", ChangeType.ADDED, new=_field("a")),
        _change("b", ChangeType.REMOVED, old=_field("b")),
    ]
    hints = build_hints(_result(changes))
    assert len(hints) == 2


def test_format_hints_text_no_changes():
    text = format_hints_text([])
    assert "No migration" in text


def test_format_hints_text_with_hints():
    f = _field("x")
    c = _change("x", ChangeType.REMOVED, old=f)
    hints = [_hint_for(c)]
    text = format_hints_text(hints)
    assert "Migration hints" in text
    assert "x" in text


def test_format_hints_dict():
    f = _field("y", required=True)
    c = _change("y", ChangeType.ADDED, new=f)
    hints = [_hint_for(c)]
    result = format_hints_dict(hints)
    assert isinstance(result, list)
    assert result[0]["field"] == "y"
    assert result[0]["change_type"] == ChangeType.ADDED.value
    assert "hint" in result[0]
    assert "example" in result[0]
