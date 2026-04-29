"""Tests for streamdiff.cli_delimit."""
import json
import os
import tempfile
from argparse import ArgumentParser, Namespace

import pytest

from streamdiff.cli_delimit import add_delimit_subparser, handle_delimit


def _write(path: str, data: dict) -> None:
    import json as _json
    with open(path, "w") as fh:
        _json.dump(data, fh)


def _parse(*argv: str) -> Namespace:
    parser = ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    add_delimit_subparser(sub)
    return parser.parse_args(["delimit", *argv])


def test_add_delimit_subparser_registers():
    parser = ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    add_delimit_subparser(sub)
    ns = parser.parse_args(["delimit", "some.json"])
    assert ns.command == "delimit"


def test_defaults():
    ns = _parse("schema.json")
    assert ns.delimiter == "."
    assert ns.depth == 1
    assert ns.output_json is False


def test_custom_delimiter():
    ns = _parse("schema.json", "--delimiter", "_")
    assert ns.delimiter == "_"


def test_custom_depth():
    ns = _parse("schema.json", "--depth", "2")
    assert ns.depth == 2


def test_json_flag():
    ns = _parse("schema.json", "--json")
    assert ns.output_json is True


def test_handle_delimit_bad_file_returns_two():
    ns = _parse("/nonexistent/schema.json")
    assert handle_delimit(ns) == 2


def test_handle_delimit_text_output(capsys):
    schema_data = {
        "name": "events",
        "fields": [
            {"name": "user.id", "type": "string", "required": True},
            {"name": "user.name", "type": "string", "required": False},
            {"name": "plain", "type": "integer", "required": True},
        ],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as fh:
        json.dump(schema_data, fh)
        path = fh.name
    try:
        ns = _parse(path)
        rc = handle_delimit(ns)
        assert rc == 0
        out = capsys.readouterr().out
        assert "user" in out
    finally:
        os.unlink(path)


def test_handle_delimit_json_output(capsys):
    schema_data = {
        "name": "events",
        "fields": [
            {"name": "order.id", "type": "string", "required": True},
        ],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as fh:
        json.dump(schema_data, fh)
        path = fh.name
    try:
        ns = _parse(path, "--json")
        rc = handle_delimit(ns)
        assert rc == 0
        data = json.loads(capsys.readouterr().out)
        assert "chunks" in data
        assert "order" in data["chunks"]
    finally:
        os.unlink(path)
