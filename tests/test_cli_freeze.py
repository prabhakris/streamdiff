import argparse
import json
import pytest
from unittest.mock import patch, MagicMock
from streamdiff.cli_freeze import add_freeze_subparser, handle_freeze
from streamdiff.freezer import FreezeRecord, FreezeResult, FreezeViolation
from streamdiff.diff import DiffResult


def _parse(args):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    add_freeze_subparser(sub)
    return parser.parse_args(args)


def test_add_freeze_subparser_registers():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    add_freeze_subparser(sub)
    ns = parser.parse_args(["freeze", "save", "schema.json", "--name", "v1"])
    assert ns.freeze_cmd == "save"


def test_save_defaults():
    ns = _parse(["freeze", "save", "s.json", "--name", "v1"])
    assert ns.schema == "s.json"
    assert ns.name == "v1"
    assert ns.dir == ".streamdiff/freezes"


def test_check_defaults():
    ns = _parse(["freeze", "check", "old.json", "new.json", "--name", "v1"])
    assert ns.old == "old.json"
    assert ns.new == "new.json"
    assert not ns.as_json


def test_handle_freeze_save_bad_file_returns_two(tmp_path):
    ns = _parse(["freeze", "save", "nonexistent.json", "--name", "v1"])
    ns.dir = str(tmp_path)
    result = handle_freeze(ns)
    assert result == 2


def test_handle_freeze_check_no_record_returns_two(tmp_path):
    schema_file = tmp_path / "s.json"
    schema_file.write_text('{"name": "s", "fields": []}')
    ns = _parse(["freeze", "check", str(schema_file), str(schema_file), "--name", "missing"])
    ns.dir = str(tmp_path / "freezes")
    result = handle_freeze(ns)
    assert result == 2


def test_handle_freeze_check_ok_returns_zero(tmp_path):
    schema_data = '{"name": "s", "fields": [{"name": "id", "type": "string", "required": true}]}'
    old_file = tmp_path / "old.json"
    new_file = tmp_path / "new.json"
    old_file.write_text(schema_data)
    new_file.write_text(schema_data)

    freeze_dir = str(tmp_path / "freezes")
    save_ns = _parse(["freeze", "save", str(old_file), "--name", "v1"])
    save_ns.dir = freeze_dir
    rc = handle_freeze(save_ns)
    assert rc == 0

    check_ns = _parse(["freeze", "check", str(old_file), str(new_file), "--name", "v1"])
    check_ns.dir = freeze_dir
    rc = handle_freeze(check_ns)
    assert rc == 0


def test_handle_freeze_check_violation_returns_one(tmp_path):
    old_data = '{"name": "s", "fields": [{"name": "id", "type": "string", "required": true}]}'
    new_data = '{"name": "s", "fields": []}'
    old_file = tmp_path / "old.json"
    new_file = tmp_path / "new.json"
    old_file.write_text(old_data)
    new_file.write_text(new_data)

    freeze_dir = str(tmp_path / "freezes")
    save_ns = _parse(["freeze", "save", str(old_file), "--name", "v1"])
    save_ns.dir = freeze_dir
    handle_freeze(save_ns)

    check_ns = _parse(["freeze", "check", str(old_file), str(new_file), "--name", "v1"])
    check_ns.dir = freeze_dir
    rc = handle_freeze(check_ns)
    assert rc == 1
