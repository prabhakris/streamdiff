import argparse
import pytest
from streamdiff.cli_stretch import add_stretch_subparser, handle_stretch
from streamdiff.schema import StreamSchema, SchemaField, FieldType
import json
import os


def _parse(args):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_stretch_subparser(sub)
    return parser.parse_args(args)


def _write(tmp_path, schema_dict):
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(schema_dict))
    return str(p)


_SIMPLE_SCHEMA = {
    "name": "events",
    "fields": [
        {"name": "user_id", "type": "string", "required": True},
        {"name": "score", "type": "integer", "required": False},
    ],
}


def test_add_stretch_subparser_registers():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_stretch_subparser(sub)
    ns = parser.parse_args(["stretch", "schema.json"])
    assert hasattr(ns, "func")


def test_add_stretch_subparser_defaults():
    ns = _parse(["stretch", "s.json"])
    assert ns.suffix == []
    assert ns.types == []
    assert ns.required is False
    assert ns.json_output is False


def test_handle_stretch_bad_file_returns_two(tmp_path):
    ns = _parse(["stretch", str(tmp_path / "missing.json"), "--suffix", "raw"])
    assert handle_stretch(ns) == 2


def test_handle_stretch_no_ops_returns_two(tmp_path):
    p = _write(tmp_path, _SIMPLE_SCHEMA)
    ns = _parse(["stretch", p])
    assert handle_stretch(ns) == 2


def test_handle_stretch_suffix_returns_zero(tmp_path):
    p = _write(tmp_path, _SIMPLE_SCHEMA)
    ns = _parse(["stretch", p, "--suffix", "raw"])
    assert handle_stretch(ns) == 0


def test_handle_stretch_types_returns_zero(tmp_path):
    p = _write(tmp_path, _SIMPLE_SCHEMA)
    ns = _parse(["stretch", p, "--types", "boolean"])
    assert handle_stretch(ns) == 0


def test_handle_stretch_unknown_type_returns_two(tmp_path):
    p = _write(tmp_path, _SIMPLE_SCHEMA)
    ns = _parse(["stretch", p, "--types", "ultratype"])
    assert handle_stretch(ns) == 2


def test_handle_stretch_json_output(tmp_path, capsys):
    p = _write(tmp_path, _SIMPLE_SCHEMA)
    ns = _parse(["stretch", p, "--suffix", "v2", "--json"])
    code = handle_stretch(ns)
    assert code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "expanded_count" in data
    assert data["expanded_count"] > data["original_count"]
