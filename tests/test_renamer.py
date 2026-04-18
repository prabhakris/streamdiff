import pytest
from streamdiff.schema import SchemaField, FieldType
from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.renamer import RenameHint, detect_renames, format_rename_hints


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = False) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _result(*changes: SchemaChange) -> DiffResult:
    return DiffResult(changes=list(changes))


def _removed(f: SchemaField) -> SchemaChange:
    return SchemaChange(field_name=f.name, change_type=ChangeType.REMOVED, old_field=f, new_field=None)


def _added(f: SchemaField) -> SchemaChange:
    return SchemaChange(field_name=f.name, change_type=ChangeType.ADDED, old_field=None, new_field=f)


def test_no_changes_returns_no_hints():
    result = _result()
    assert detect_renames(result) == []


def test_obvious_rename_detected():
    old = _field("user_id", FieldType.STRING)
    new = _field("user_identifier", FieldType.STRING)
    result = _result(_removed(old), _added(new))
    hints = detect_renames(result, min_confidence=0.3)
    assert len(hints) == 1
    assert hints[0].old_name == "user_id"
    assert hints[0].new_name == "user_identifier"


def test_type_mismatch_not_suggested():
    old = _field("count", FieldType.INTEGER)
    new = _field("count_str", FieldType.STRING)
    result = _result(_removed(old), _added(new))
    hints = detect_renames(result, min_confidence=0.1)
    assert hints == []


def test_low_confidence_filtered_out():
    old = _field("abc", FieldType.INTEGER)
    new = _field("xyz", FieldType.INTEGER)
    result = _result(_removed(old), _added(new))
    hints = detect_renames(result, min_confidence=0.9)
    assert hints == []


def test_confidence_within_range():
    old = _field("event_time", FieldType.STRING)
    new = _field("event_timestamp", FieldType.STRING)
    result = _result(_removed(old), _added(new))
    hints = detect_renames(result, min_confidence=0.3)
    for h in hints:
        assert 0.0 <= h.confidence <= 1.0


def test_format_no_hints():
    assert format_rename_hints([]) == "No rename hints detected."


def test_format_with_hints():
    hints = [RenameHint("old_name", "new_name", 0.75)]
    text = format_rename_hints(hints)
    assert "Possible renames:" in text
    assert "old_name -> new_name" in text
    assert "75%" in text


def test_str_hint():
    h = RenameHint("a", "b", 0.5)
    assert str(h) == "a -> b (50% confidence)"
