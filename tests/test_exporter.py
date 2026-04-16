"""Tests for streamdiff.exporter."""
import json
import csv
import io
import pytest

from streamdiff.schema import SchemaField, FieldType, StreamSchema
from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.exporter import export_json, export_csv, write_export


def _field(name: str, ftype: str = "string", required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType(ftype), required=required)


def _result(*changes: SchemaChange) -> DiffResult:
    return DiffResult(changes=list(changes))


def _change(ct: ChangeType, name: str, old=None, new=None, breaking=False) -> SchemaChange:
    return SchemaChange(change_type=ct, field_name=name, old_field=old, new_field=new, is_breaking=breaking)


def test_export_json_no_changes():
    result = _result()
    out = export_json(result)
    data = json.loads(out)
    assert data["changes"] == []
    assert "summary" in data


def test_export_json_added_field():
    f = _field("age", "integer", required=False)
    c = _change(ChangeType.ADDED, "age", new=f)
    data = json.loads(export_json(_result(c)))
    assert len(data["changes"]) == 1
    assert data["changes"][0]["change_type"] == "added"
    assert data["changes"][0]["field_name"] == "age"
    assert data["changes"][0]["is_breaking"] is False
    assert data["changes"][0]["old_field"] is None


def test_export_json_breaking_change():
    old = _field("score", "integer")
    new = _field("score", "string")
    c = _change(ChangeType.MODIFIED, "score", old=old, new=new, breaking=True)
    data = json.loads(export_json(_result(c)))
    assert data["changes"][0]["is_breaking"] is True
    assert data["summary"]["breaking"] == 1


def test_export_csv_headers():
    result = _result()
    out = export_csv(result)
    reader = csv.DictReader(io.StringIO(out))
    assert set(reader.fieldnames) == {"change_type", "field_name", "is_breaking", "old_type", "new_type"}


def test_export_csv_row():
    f = _field("email", "string")
    c = _change(ChangeType.REMOVED, "email", old=f, breaking=True)
    out = export_csv(_result(c))
    rows = list(csv.DictReader(io.StringIO(out)))
    assert len(rows) == 1
    assert rows[0]["field_name"] == "email"
    assert rows[0]["change_type"] == "removed"
    assert rows[0]["old_type"] == "string"
    assert rows[0]["new_type"] == ""


def test_write_export_json(tmp_path):
    result = _result()
    out_file = tmp_path / "out.json"
    write_export(result, "json", str(out_file))
    data = json.loads(out_file.read_text())
    assert "changes" in data


def test_write_export_csv(tmp_path):
    result = _result()
    out_file = tmp_path / "out.csv"
    write_export(result, "csv", str(out_file))
    assert "change_type" in out_file.read_text()


def test_write_export_invalid_format():
    with pytest.raises(ValueError, match="Unsupported"):
        write_export(_result(), "xml", "/tmp/x.xml")
