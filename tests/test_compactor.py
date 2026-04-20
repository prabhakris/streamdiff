"""Tests for streamdiff.compactor."""
from __future__ import annotations

import pytest

from streamdiff.schema import SchemaField, FieldType, StreamSchema
from streamdiff.diff import SchemaChange, ChangeType, DiffResult
from streamdiff.compactor import compact_changes, compact_result, CompactResult


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(name: str, change_type: ChangeType) -> SchemaChange:
    f = _field(name)
    return SchemaChange(field_name=name, change_type=change_type, old_field=f, new_field=f)


def _result(changes):
    schema = StreamSchema(name="s", fields=[])
    return DiffResult(old_schema=schema, new_schema=schema, changes=changes)


# ---------------------------------------------------------------------------
# compact_changes
# ---------------------------------------------------------------------------

def test_no_changes_returns_empty_compact():
    result = compact_changes([])
    assert result.original_count == 0
    assert result.compacted == []
    assert not result


def test_unique_changes_all_kept():
    changes = [
        _change("a", ChangeType.ADDED),
        _change("b", ChangeType.REMOVED),
    ]
    result = compact_changes(changes)
    assert result.original_count == 2
    assert len(result.compacted) == 2


def test_duplicate_field_keeps_higher_priority():
    """TYPE_CHANGED beats ADDED for the same field name."""
    changes = [
        _change("x", ChangeType.ADDED),
        _change("x", ChangeType.TYPE_CHANGED),
    ]
    result = compact_changes(changes)
    assert len(result.compacted) == 1
    assert result.compacted[0].change_type == ChangeType.TYPE_CHANGED


def test_removed_beats_added():
    changes = [
        _change("y", ChangeType.ADDED),
        _change("y", ChangeType.REMOVED),
    ]
    result = compact_changes(changes)
    assert result.compacted[0].change_type == ChangeType.REMOVED


def test_type_changed_beats_removed():
    changes = [
        _change("z", ChangeType.REMOVED),
        _change("z", ChangeType.TYPE_CHANGED),
    ]
    result = compact_changes(changes)
    assert result.compacted[0].change_type == ChangeType.TYPE_CHANGED


def test_original_count_reflects_input_length():
    changes = [_change("a", ChangeType.ADDED)] * 5
    result = compact_changes(changes)
    assert result.original_count == 5
    assert len(result.compacted) == 1


# ---------------------------------------------------------------------------
# compact_result convenience wrapper
# ---------------------------------------------------------------------------

def test_compact_result_wrapper():
    diff = _result([
        _change("field1", ChangeType.ADDED),
        _change("field1", ChangeType.TYPE_CHANGED),
        _change("field2", ChangeType.REMOVED),
    ])
    cr = compact_result(diff)
    assert cr.original_count == 3
    assert len(cr.compacted) == 2


# ---------------------------------------------------------------------------
# to_dict / __str__
# ---------------------------------------------------------------------------

def test_to_dict_keys():
    result = compact_changes([_change("a", ChangeType.ADDED)])
    d = result.to_dict()
    assert "original_count" in d
    assert "compacted_count" in d
    assert "changes" in d
    assert d["compacted_count"] == 1


def test_str_no_changes():
    result = compact_changes([])
    assert "no changes" in str(result)


def test_str_with_changes():
    result = compact_changes([_change("myfield", ChangeType.REMOVED)])
    text = str(result)
    assert "myfield" in text
    assert "removed" in text
