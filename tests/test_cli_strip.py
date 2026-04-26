"""Tests for streamdiff.cli_strip."""
import argparse
import json
import os
import tempfile

import pytest

from streamdiff.cli_strip import add_strip_subparser, handle_strip
from streamdiff.schema import FieldType, SchemaField, StreamSchema


def _write(tmp_dir: str, data: dict, name: str = "schema.json") -> str:
    path = os.path.join(tmp_dir, name)
    with open(path, "w") as fh:
        json.dump(data, fh)
    return path


def _schema_json(*fields) -> dict:
    return {"fields": list(fields)}


def _parse(args):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    add_strip_subparser(sub)
    return parser.parse_args(args)


# ---------------------------------------------------------------------------
# parser registration
# ---------------------------------------------------------------------------

def test_add_strip_subparser_registers():
    ns = _parse(["strip", "some_file.json", "--required"])
    assert ns.command == "strip"


def test_add_strip_subparser_defaults():
    ns = _parse(["strip", "f.json", "--required"])
    assert ns.required is True
    assert ns.fields is None
    assert ns.output_json is False


def test_add_strip_subparser_fields_flag():
    ns = _parse(["strip", "f.json", "--fields", "a", "b"])
    assert ns.fields == ["a", "b"]


def test_add_strip_subparser_json_flag():
    ns = _parse(["strip", "f.json", "--required", "--json"])
    assert ns.output_json is True


# ---------------------------------------------------------------------------
# handle_strip
# ---------------------------------------------------------------------------

def test_handle_strip_bad_file_returns_two():
    ns = _parse(["strip", "/nonexistent/schema.json", "--required"])
    assert handle_strip(ns) == 2


def test_handle_strip_no_mode_returns_two(tmp_path):
    path = _write(str(tmp_path), _schema_json({"name": "a", "type": "string", "required": True}))
    ns = _parse(["strip", path])
    # neither --required nor --fields supplied
    assert handle_strip(ns) == 2


def test_handle_strip_required_returns_zero(tmp_path, capsys):
    path = _write(
        str(tmp_path),
        _schema_json(
            {"name": "a", "type": "string", "required": True},
            {"name": "b", "type": "integer", "required": True},
        ),
    )
    ns = _parse(["strip", path, "--required"])
    code = handle_strip(ns)
    assert code == 0


def test_handle_strip_fields_returns_zero(tmp_path, capsys):
    path = _write(
        str(tmp_path),
        _schema_json(
            {"name": "a", "type": "string", "required": True},
            {"name": "b", "type": "integer", "required": False},
        ),
    )
    ns = _parse(["strip", path, "--fields", "a"])
    code = handle_strip(ns)
    assert code == 0


def test_handle_strip_json_output(tmp_path, capsys):
    path = _write(
        str(tmp_path),
        _schema_json({"name": "x", "type": "string", "required": True}),
    )
    ns = _parse(["strip", path, "--required", "--json"])
    handle_strip(ns)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "original_count" in data
    assert "stripped_count" in data
    assert "removed_attrs" in data
