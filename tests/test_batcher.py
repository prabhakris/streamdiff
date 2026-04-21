"""Tests for streamdiff.batcher."""
import pytest

from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType
from streamdiff.batcher import (
    BatchEntry,
    BatchReport,
    batch_results,
    breaking_entries,
)


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(name: str, change_type: ChangeType, breaking: bool) -> SchemaChange:
    return SchemaChange(field_name=name, change_type=change_type, breaking=breaking)


def _result(*changes: SchemaChange) -> DiffResult:
    return DiffResult(changes=list(changes))


def test_batch_results_empty():
    report = batch_results([])
    assert not report
    assert report.total_changes() == 0
    assert not report.has_breaking()


def test_batch_results_single_no_changes():
    report = batch_results([("stream-a", _result())])
    assert len(report.entries) == 1
    assert report.total_changes() == 0
    assert not report.has_breaking()


def test_batch_results_counts_changes():
    r1 = _result(_change("x", ChangeType.ADDED, False))
    r2 = _result(
        _change("y", ChangeType.REMOVED, True),
        _change("z", ChangeType.TYPE_CHANGED, True),
    )
    report = batch_results([("a", r1), ("b", r2)])
    assert report.total_changes() == 3


def test_batch_results_has_breaking_when_any_breaking():
    r1 = _result(_change("x", ChangeType.ADDED, False))
    r2 = _result(_change("y", ChangeType.REMOVED, True))
    report = batch_results([("a", r1), ("b", r2)])
    assert report.has_breaking()


def test_batch_results_no_breaking_when_all_safe():
    r1 = _result(_change("x", ChangeType.ADDED, False))
    r2 = _result(_change("z", ChangeType.ADDED, False))
    report = batch_results([("a", r1), ("b", r2)])
    assert not report.has_breaking()


def test_breaking_entries_filters_correctly():
    r_safe = _result(_change("x", ChangeType.ADDED, False))
    r_break = _result(_change("y", ChangeType.REMOVED, True))
    report = batch_results([("safe", r_safe), ("danger", r_break)])
    broken = breaking_entries(report)
    assert len(broken) == 1
    assert broken[0].name == "danger"


def test_breaking_entries_empty_when_no_breaking():
    r = _result(_change("x", ChangeType.ADDED, False))
    report = batch_results([("a", r)])
    assert breaking_entries(report) == []


def test_to_dict_structure():
    r = _result(_change("f", ChangeType.REMOVED, True))
    report = batch_results([("stream-x", r)])
    d = report.to_dict()
    assert d["total_entries"] == 1
    assert d["total_changes"] == 1
    assert d["has_breaking"] is True
    assert d["entries"][0]["name"] == "stream-x"


def test_by_name_lookup():
    r = _result()
    report = batch_results([("my-stream", r)])
    lookup = report.by_name()
    assert "my-stream" in lookup
    assert lookup["my-stream"].result is r


def test_entry_str_no_breaking():
    e = BatchEntry(name="s", result=_result(_change("a", ChangeType.ADDED, False)))
    assert "[BREAKING]" not in str(e)
    assert "s" in str(e)


def test_entry_str_breaking():
    e = BatchEntry(name="s", result=_result(_change("a", ChangeType.REMOVED, True)))
    assert "[BREAKING]" in str(e)
