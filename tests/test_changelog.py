"""Tests for streamdiff.changelog."""
import json
from pathlib import Path

import pytest

from streamdiff.changelog import (
    ChangelogEntry,
    build_entry,
    append_changelog,
    load_changelog,
)
from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType


def _field(name: str, required: bool = False) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(name: str, ct: ChangeType) -> SchemaChange:
    f = _field(name)
    return SchemaChange(field_name=name, change_type=ct, old_field=f, new_field=f)


def _result(*changes: SchemaChange) -> DiffResult:
    return DiffResult(changes=list(changes))


def test_build_entry_no_changes():
    entry = build_entry(_result(), stream="my-stream")
    assert entry.stream == "my-stream"
    assert entry.added == []
    assert entry.removed == []
    assert entry.modified == []
    assert entry.breaking is False


def test_build_entry_added_field():
    entry = build_entry(_result(_change("foo", ChangeType.ADDED)), stream="s")
    assert "foo" in entry.added


def test_build_entry_removed_field_is_breaking():
    c = SchemaChange(
        field_name="bar",
        change_type=ChangeType.REMOVED,
        old_field=_field("bar"),
        new_field=None,
    )
    entry = build_entry(_result(c), stream="s")
    assert "bar" in entry.removed
    assert entry.breaking is True


def test_to_text_no_changes():
    entry = ChangelogEntry(timestamp="2024-01-01T00:00:00Z", stream="s", breaking=False)
    text = entry.to_text()
    assert "(no changes)" in text


def test_to_text_shows_symbols():
    entry = ChangelogEntry(
        timestamp="2024-01-01T00:00:00Z",
        stream="s",
        breaking=True,
        added=["a"],
        removed=["b"],
        modified=["c"],
    )
    text = entry.to_text()
    assert "+ a" in text
    assert "- b" in text
    assert "~ c" in text
    assert "BREAKING" in text


def test_append_and_load(tmp_path):
    p = tmp_path / "changelog.json"
    e1 = ChangelogEntry("2024-01-01T00:00:00Z", "s", False, added=["x"])
    e2 = ChangelogEntry("2024-01-02T00:00:00Z", "s", True, removed=["y"])
    append_changelog(e1, p)
    append_changelog(e2, p)
    entries = load_changelog(p)
    assert len(entries) == 2
    assert entries[0].added == ["x"]
    assert entries[1].breaking is True


def test_load_missing_file(tmp_path):
    assert load_changelog(tmp_path / "nope.json") == []
