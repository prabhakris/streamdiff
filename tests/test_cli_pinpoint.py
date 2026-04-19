import argparse
import pytest
from unittest.mock import patch, MagicMock
from streamdiff.cli_pinpoint import add_pinpoint_subparser, handle_pinpoint
from streamdiff.pinpointer import PinpointReport, Pinpoint
from streamdiff.diff import ChangeType


def _parse(args):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_pinpoint_subparser(sub)
    return parser.parse_args(args)


def test_add_pinpoint_subparser_registers():
    ns = _parse(["pinpoint", "a.json", "b.json"])
    assert ns.old_schema == "a.json"
    assert ns.new_schema == "b.json"
    assert ns.as_json is False


def test_add_pinpoint_subparser_json_flag():
    ns = _parse(["pinpoint", "a.json", "b.json", "--json"])
    assert ns.as_json is True


def test_handle_pinpoint_bad_file_returns_two():
    ns = _parse(["pinpoint", "missing_a.json", "missing_b.json"])
    result = handle_pinpoint(ns)
    assert result == 2


def test_handle_pinpoint_no_changes(tmp_path, capsys):
    schema = '{"fields": [{"name": "id", "type": "string", "required": true}]}'
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(schema)
    b.write_text(schema)
    ns = _parse(["pinpoint", str(a), str(b)])
    rc = handle_pinpoint(ns)
    out = capsys.readouterr().out
    assert rc == 0
    assert "No changes" in out


def test_handle_pinpoint_json_output(tmp_path, capsys):
    schema = '{"fields": [{"name": "id", "type": "string", "required": true}]}'
    schema2 = '{"fields": [{"name": "id", "type": "string", "required": true}, {"name": "email", "type": "string", "required": false}]}'
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(schema)
    b.write_text(schema2)
    ns = _parse(["pinpoint", str(a), str(b), "--json"])
    rc = handle_pinpoint(ns)
    out = capsys.readouterr().out
    import json
    data = json.loads(out)
    assert rc == 0
    assert "pinpoints" in data
