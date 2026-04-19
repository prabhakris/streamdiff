import json
import pytest
from streamdiff.freezer import (
    save_freeze, load_freeze, check_freeze, freeze_path, FreezeViolation
)
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.diff import DiffResult, SchemaChange, ChangeType


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _schema(*names: str) -> StreamSchema:
    fields = [_field(n) for n in names]
    return StreamSchema(name="test", fields=fields)


def _change(name: str, ct: ChangeType = ChangeType.REMOVED) -> SchemaChange:
    return SchemaChange(field_name=name, change_type=ct, old_field=_field(name), new_field=None)


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


def test_save_creates_file(tmp_dir):
    schema = _schema("id", "name")
    record = save_freeze(schema, "v1", tmp_dir)
    assert freeze_path(tmp_dir, "v1").exists()
    assert record.name == "v1"
    assert sorted(record.fields) == ["id", "name"]


def test_save_content_is_valid_json(tmp_dir):
    schema = _schema("id")
    save_freeze(schema, "v1", tmp_dir)
    data = json.loads(freeze_path(tmp_dir, "v1").read_text())
    assert data["name"] == "v1"
    assert "id" in data["fields"]


def test_load_returns_none_when_missing(tmp_dir):
    result = load_freeze("nonexistent", tmp_dir)
    assert result is None


def test_load_roundtrip(tmp_dir):
    schema = _schema("a", "b", "c")
    save_freeze(schema, "myfreeze", tmp_dir)
    record = load_freeze("myfreeze", tmp_dir)
    assert record is not None
    assert record.name == "myfreeze"
    assert set(record.fields) == {"a", "b", "c"}


def test_check_freeze_no_changes_passes(tmp_dir):
    schema = _schema("id", "name")
    record = save_freeze(schema, "v1", tmp_dir)
    diff = DiffResult(changes=[])
    result = check_freeze(record, diff)
    assert result.ok()
    assert result.violations == []


def test_check_freeze_detects_violation(tmp_dir):
    schema = _schema("id", "name")
    record = save_freeze(schema, "v1", tmp_dir)
    diff = DiffResult(changes=[_change("id", ChangeType.REMOVED)])
    result = check_freeze(record, diff)
    assert not result.ok()
    assert len(result.violations) == 1
    assert "id" in str(result.violations[0])


def test_check_freeze_ignores_non_frozen_fields(tmp_dir):
    schema = _schema("id")
    record = save_freeze(schema, "v1", tmp_dir)
    diff = DiffResult(changes=[_change("extra", ChangeType.ADDED)])
    result = check_freeze(record, diff)
    assert result.ok()


def test_freeze_result_to_dict(tmp_dir):
    schema = _schema("id")
    record = save_freeze(schema, "v1", tmp_dir)
    diff = DiffResult(changes=[])
    result = check_freeze(record, diff)
    d = result.to_dict()
    assert d["ok"] is True
    assert "record" in d
    assert "violations" in d
