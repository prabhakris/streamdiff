"""Tests for streamdiff.formatter."""
import pytest

from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.schema import FieldType, SchemaField
from streamdiff.formatter import build_summary, format_summary_text, format_summary_dict


def _field(name: str, required: bool = False) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(change_type: ChangeType, breaking: bool = False) -> SchemaChange:
    return SchemaChange(
        field_name="f",
        change_type=change_type,
        old_field=_field("f"),
        new_field=_field("f"),
        breaking=breaking,
    )


def _result(*changes: SchemaChange) -> DiffResult:
    return DiffResult(changes=list(changes), has_breaking=any(c.breaking for c in changes))


def test_build_summary_no_changes():
    result = _result()
    summary = build_summary(result)
    assert all(s.count == 0 for s in summary)


def test_build_summary_counts():
    result = _result(
        _change(ChangeType.ADDED),
        _change(ChangeType.ADDED),
        _change(ChangeType.REMOVED, breaking=True),
        _change(ChangeType.TYPE_CHANGED, breaking=True),
    )
    counts = {s.label: s.count for s in build_summary(result)}
    assert counts["added"] == 2
    assert counts["removed"] == 1
    assert counts["modified"] == 1
    assert counts["breaking"] == 2


def test_format_summary_text_contains_header():
    result = _result(_change(ChangeType.ADDED))
    text = format_summary_text(result)
    assert "Schema diff summary" in text
    assert "1 change(s)" in text


def test_format_summary_text_shows_counts():
    result = _result(_change(ChangeType.ADDED), _change(ChangeType.REMOVED, breaking=True))
    text = format_summary_text(result)
    assert "added: 1" in text
    assert "removed: 1" in text
    assert "breaking: 1" in text


def test_format_summary_dict_structure():
    result = _result(_change(ChangeType.REMOVED, breaking=True))
    d = format_summary_dict(result)
    assert d["total_changes"] == 1
    assert d["has_breaking"] is True
    assert "counts" in d
    assert d["counts"]["removed"] == 1


def test_format_summary_dict_no_changes():
    result = _result()
    d = format_summary_dict(result)
    assert d["total_changes"] == 0
    assert d["has_breaking"] is False
    assert all(v == 0 for v in d["counts"].values())
