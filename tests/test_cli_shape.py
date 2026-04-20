"""Tests for streamdiff.cli_shape."""
import argparse
import json
import os
import tempfile

import pytest

from streamdiff.cli_shape import add_shape_subparser, handle_shape


def _write(tmp_dir: str, name: str, data: dict) -> str:
    path = os.path.join(tmp_dir, name)
    with open(path, "w") as fh:
        json.dump(data, fh)
    return path


def _parse(args):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_shape_subparser(sub)
    return parser.parse_args(args)


@pytest.fixture()
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture()
def schema_file(tmp_dir):
    return _write(
        tmp_dir,
        "schema.json",
        {
            "name": "test",
            "fields": [
                {"name": "id", "type": "string", "required": False},
                {"name": "ts", "type": "string", "required": True},
            ],
        },
    )


def test_add_shape_subparser_registers():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_shape_subparser(sub)
    ns = parser.parse_args(["shape", "somefile.json"])
    assert ns.schema == "somefile.json"


def test_add_shape_subparser_defaults():
    ns = _parse(["shape", "f.json"])
    assert ns.transforms == []
    assert ns.json is False
    assert ns.list_transforms is False


def test_handle_shape_bad_file_returns_two():
    ns = _parse(["shape", "/no/such/file.json"])
    assert handle_shape(ns) == 2


def test_handle_shape_no_transforms_returns_zero(schema_file):
    ns = _parse(["shape", schema_file])
    assert handle_shape(ns) == 0


def test_handle_shape_require_all_returns_zero(schema_file):
    ns = _parse(["shape", schema_file, "--transforms", "require_all"])
    assert handle_shape(ns) == 0


def test_handle_shape_json_flag(schema_file, capsys):
    ns = _parse(["shape", schema_file, "--transforms", "require_all", "--json"])
    handle_shape(ns)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "applied" in data
    assert "skipped" in data


def test_handle_shape_list_transforms_returns_zero(schema_file, capsys):
    ns = _parse(["shape", schema_file, "--list-transforms"])
    rc = handle_shape(ns)
    assert rc == 0
    out = capsys.readouterr().out
    assert "require_all" in out
    assert "optional_all" in out
