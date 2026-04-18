import pytest
from streamdiff.schema import SchemaField, FieldType
from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.summarizer import summarize, DiffSummary


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(name: str, change_type: ChangeType, is_breaking: bool = False) -> SchemaChange:
    return SchemaChange(
        field_name=name,
        change_type=change_type,
        old_field=_field(name),
        new_field=_field(name),
        is_breaking=is_breaking,
    )


def _result(changes):
    return DiffResult(changes=changes)


def test_no_changes_returns_zero_summary():
    s = summarize(_result([]))
    assert s.total == 0
    assert s.added == 0
    assert s.removed == 0
    assert s.type_changed == 0
    assert s.breaking == 0


def test_added_field_counted():
    s = summarize(_result([_change("x", ChangeType.ADDED)]))
    assert s.total == 1
    assert s.added == 1
    assert s.removed == 0


def test_removed_field_counted():
    s = summarize(_result([_change("x", ChangeType.REMOVED, is_breaking=True)]))
    assert s.removed == 1
    assert s.breaking == 1


def test_type_changed_counted():
    s = summarize(_result([_change("x", ChangeType.TYPE_CHANGED, is_breaking=True)]))
    assert s.type_changed == 1
    assert s.breaking == 1


def test_mixed_changes():
    changes = [
        _change("a", ChangeType.ADDED),
        _change("b", ChangeType.REMOVED, is_breaking=True),
        _change("c", ChangeType.TYPE_CHANGED, is_breaking=True),
    ]
    s = summarize(_result(changes))
    assert s.total == 3
    assert s.added == 1
    assert s.removed == 1
    assert s.type_changed == 1
    assert s.breaking == 2


def test_by_type_counts():
    changes = [
        _change("a", ChangeType.ADDED),
        _change("b", ChangeType.ADDED),
        _change("c", ChangeType.REMOVED, is_breaking=True),
    ]
    s = summarize(_result(changes))
    assert s.by_type[ChangeType.ADDED.value] == 2
    assert s.by_type[ChangeType.REMOVED.value] == 1


def test_to_dict_keys():
    s = summarize(_result([]))
    d = s.to_dict()
    assert set(d.keys()) == {"total", "added", "removed", "type_changed", "breaking", "by_type"}


def test_str_contains_totals():
    s = DiffSummary(total=3, added=1, removed=1, type_changed=1, breaking=2)
    text = str(s)
    assert "3" in text
    assert "Breaking" in text
