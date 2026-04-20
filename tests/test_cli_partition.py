import json
import os
import tempfile
import pytest

from streamdiff.cli_partition import add_partition_subparser, handle_partition
from streamdiff.schema import StreamSchema, SchemaField, FieldType
import argparse


def _schema_json(fields):
    return json.dumps({"name": "test", "fields": fields})


def _write(tmp_path, content):
    p = os.path.join(tmp_path, "schema.json")
    with open(p, "w") as f:
        f.write(content)
    return p


def _parse(args):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_partition_subparser(sub)
    return parser.parse_args(args)


def test_add_partition_subparser_registers():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_partition_subparser(sub)
    ns = parser.parse_args(["partition", "schema.json"])
    assert ns.strategy == "required"
    assert ns.separator == "_"
    assert ns.output_json is False


def test_add_partition_subparser_json_flag():
    ns = _parse(["partition", "schema.json", "--json"])
    assert ns.output_json is True


def test_add_partition_subparser_strategy_type():
    ns = _parse(["partition", "schema.json", "--strategy", "type"])
    assert ns.strategy == "type"


def test_handle_partition_bad_file_returns_two(tmp_path):
    ns = _parse(["partition", "/nonexistent/schema.json"])
    assert handle_partition(ns) == 2


def test_handle_partition_required_strategy_returns_zero(tmp_path, capsys):
    path = _write(
        str(tmp_path),
        _schema_json([
            {"name": "id", "type": "string", "required": True},
            {"name": "label", "type": "string", "required": False},
        ]),
    )
    ns = _parse(["partition", path])
    code = handle_partition(ns)
    assert code == 0
    out = capsys.readouterr().out
    assert "required" in out


def test_handle_partition_json_output(tmp_path, capsys):
    path = _write(
        str(tmp_path),
        _schema_json([{"name": "user_id", "type": "string", "required": True}]),
    )
    ns = _parse(["partition", path, "--json"])
    code = handle_partition(ns)
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert "strategy" in data
    assert "partitions" in data


def test_handle_partition_prefix_strategy(tmp_path, capsys):
    path = _write(
        str(tmp_path),
        _schema_json([
            {"name": "user_id", "type": "string", "required": True},
            {"name": "user_name", "type": "string", "required": True},
            {"name": "order_id", "type": "string", "required": True},
        ]),
    )
    ns = _parse(["partition", path, "--strategy", "prefix"])
    code = handle_partition(ns)
    assert code == 0
    out = capsys.readouterr().out
    assert "user" in out
    assert "order" in out
