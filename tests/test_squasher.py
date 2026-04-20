import pytest
from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType
from streamdiff.squasher import squash, SquashResult


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(name: str, ct: ChangeType, breaking: bool = False) -> SchemaChange:
    return SchemaChange(field_name=name, change_type=ct, field=_field(name), breaking=breaking)


def _result(*changes: SchemaChange) -> DiffResult:
    return DiffResult(changes=list(changes))


def test_squash_empty_list_returns_empty():
    result = squash([])
    assert isinstance(result, SquashResult)
    assert not result
    assert result.source_count == 0
    assert result.changes == []


def test_squash_single_result_no_changes():
    result = squash([_result()])
    assert result.source_count == 1
    assert result.changes == []


def test_squash_single_result_with_changes():
    c = _change("user_id", ChangeType.ADDED)
    result = squash([_result(c)])
    assert result.source_count == 1
    assert len(result.changes) == 1
    assert result.changes[0].field_name == "user_id"


def test_squash_deduplicates_same_change():
    c1 = _change("email", ChangeType.REMOVED, breaking=False)
    c2 = _change("email", ChangeType.REMOVED, breaking=True)
    result = squash([_result(c1), _result(c2)])
    assert len(result.changes) == 1
    assert result.changes[0].breaking is True


def test_squash_keeps_distinct_changes():
    c1 = _change("email", ChangeType.ADDED)
    c2 = _change("phone", ChangeType.REMOVED, breaking=True)
    result = squash([_result(c1), _result(c2)])
    assert len(result.changes) == 2


def test_squash_source_count():
    result = squash([_result(), _result(), _result()])
    assert result.source_count == 3


def test_squash_to_dict():
    c = _change("age", ChangeType.TYPE_CHANGED, breaking=True)
    result = squash([_result(c)])
    d = result.to_dict()
    assert d["source_count"] == 1
    assert d["change_count"] == 1
    assert d["changes"][0]["field"] == "age"
    assert d["changes"][0]["breaking"] is True


def test_squash_str_no_changes():
    result = squash([_result()])
    assert "no changes" in str(result)


def test_squash_str_with_changes():
    c = _change("id", ChangeType.REMOVED, breaking=True)
    result = squash([_result(c)])
    out = str(result)
    assert "BREAKING" in out
    assert "id" in out
