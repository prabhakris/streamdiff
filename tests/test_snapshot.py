"""Tests for streamdiff.snapshot."""
import json
import os
import pytest

from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.snapshot import (
    save_snapshot,
    load_snapshot,
    list_snapshots,
    delete_snapshot,
    snapshot_path,
)


def _schema(*fields):
    return StreamSchema(list(fields))


def _field(name, ftype=FieldType.STRING, required=True):
    return SchemaField(name=name, field_type=ftype, required=required)


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path / "snaps")


def test_save_creates_file(tmp_dir):
    s = _schema(_field("id"), _field("name"))
    path = save_snapshot(s, "v1", directory=tmp_dir)
    assert os.path.exists(path)


def test_save_content_is_valid_json(tmp_dir):
    s = _schema(_field("id"))
    path = save_snapshot(s, "v1", directory=tmp_dir)
    with open(path) as fh:
        data = json.load(fh)
    assert data["name"] == "v1"
    assert len(data["fields"]) == 1
    assert data["fields"][0]["name"] == "id"


def test_save_with_metadata(tmp_dir):
    s = _schema(_field("x"))
    path = save_snapshot(s, "v2", directory=tmp_dir, metadata={"env": "prod"})
    with open(path) as fh:
        data = json.load(fh)
    assert data["metadata"]["env"] == "prod"


def test_load_snapshot_returns_schema(tmp_dir):
    s = _schema(_field("id"), _field("ts", FieldType.LONG))
    save_snapshot(s, "base", directory=tmp_dir)
    loaded = load_snapshot("base", directory=tmp_dir)
    assert len(loaded.fields) == 2
    assert loaded.fields[0].name == "id"


def test_load_missing_raises(tmp_dir):
    with pytest.raises(FileNotFoundError, match="missing"):
        load_snapshot("missing", directory=tmp_dir)


def test_list_snapshots_empty(tmp_dir):
    assert list_snapshots(tmp_dir) == []


def test_list_snapshots_returns_names(tmp_dir):
    s = _schema(_field("a"))
    save_snapshot(s, "alpha", directory=tmp_dir)
    save_snapshot(s, "beta", directory=tmp_dir)
    names = list_snapshots(tmp_dir)
    assert "alpha" in names
    assert "beta" in names


def test_delete_snapshot(tmp_dir):
    s = _schema(_field("a"))
    save_snapshot(s, "temp", directory=tmp_dir)
    assert delete_snapshot("temp", directory=tmp_dir) is True
    assert "temp" not in list_snapshots(tmp_dir)


def test_delete_missing_returns_false(tmp_dir):
    assert delete_snapshot("ghost", directory=tmp_dir) is False
