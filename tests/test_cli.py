"""Tests for the CLI entry point."""
import json
from pathlib import Path
import pytest

from streamdiff.cli import main


OLD_SCHEMA = {
    "name": "UserEvent",
    "fields": [
        {"name": "id", "type": "string", "required": True},
        {"name": "email", "type": "string", "required": False},
    ],
}

NEW_SCHEMA_SAFE = {
    "name": "UserEvent",
    "fields": [
        {"name": "id", "type": "string", "required": True},
        {"name": "email", "type": "string", "required": False},
        {"name": "age", "type": "integer", "required": False},
    ],
}

NEW_SCHEMA_BREAKING = {
    "name": "UserEvent",
    "fields": [
        {"name": "id", "type": "string", "required": True},
    ],
}


@pytest.fixture
def schema_files(tmp_path):
    def _write(name, data):
        p = tmp_path / name
        p.write_text(json.dumps(data))
        return p
    return _write


def test_no_changes_exits_zero(schema_files):
    old = schema_files("old.json", OLD_SCHEMA)
    new = schema_files("new.json", OLD_SCHEMA)
    assert main([str(old), str(new)]) == 0


def test_safe_change_exits_zero(schema_files):
    old = schema_files("old.json", OLD_SCHEMA)
    new = schema_files("new.json", NEW_SCHEMA_SAFE)
    assert main([str(old), str(new)]) == 0


def test_breaking_change_exits_one(schema_files):
    old = schema_files("old.json", OLD_SCHEMA)
    new = schema_files("new.json", NEW_SCHEMA_BREAKING)
    assert main([str(old), str(new)]) == 1


def test_strict_mode_exits_one_on_any_change(schema_files):
    old = schema_files("old.json", OLD_SCHEMA)
    new = schema_files("new.json", NEW_SCHEMA_SAFE)
    assert main([str(old), str(new), "--strict"]) == 1


def test_missing_file_exits_two(schema_files, tmp_path):
    old = schema_files("old.json", OLD_SCHEMA)
    assert main([str(old), str(tmp_path / "missing.json")]) == 2


def test_json_output(schema_files, capsys):
    old = schema_files("old.json", OLD_SCHEMA)
    new = schema_files("new.json", NEW_SCHEMA_BREAKING)
    main([str(old), str(new), "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["breaking"] is True
    assert any(c["type"] == "removed" for c in data["changes"])
