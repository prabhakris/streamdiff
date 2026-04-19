import json
import pytest
from unittest.mock import patch, MagicMock
from streamdiff.cli_embed import add_embed_subparser, handle_embed
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.embedder import EmbedReport, EmbedVector
import argparse


def _parse(args: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_embed_subparser(sub)
    return parser.parse_args(args)


def _schema(*names: str) -> StreamSchema:
    fields = [SchemaField(name=n, type=FieldType.STRING, required=True) for n in names]
    return StreamSchema(name="s", fields=fields)


def test_add_embed_subparser_registers():
    ns = _parse(["embed", "schema.json"])
    assert ns.schema == "schema.json"
    assert ns.as_json is False
    assert ns.field_name is None


def test_add_embed_subparser_json_flag():
    ns = _parse(["embed", "schema.json", "--json"])
    assert ns.as_json is True


def test_add_embed_subparser_field_flag():
    ns = _parse(["embed", "schema.json", "--field", "age"])
    assert ns.field_name == "age"


def test_handle_embed_bad_file_returns_two(tmp_path):
    ns = _parse(["embed", str(tmp_path / "missing.json")])
    assert handle_embed(ns) == 2


def test_handle_embed_no_changes_returns_zero(tmp_path):
    schema_file = tmp_path / "s.json"
    schema_file.write_text(json.dumps({"name": "s", "fields": []}))
    ns = _parse(["embed", str(schema_file)])
    assert handle_embed(ns) == 0


def test_handle_embed_json_output(tmp_path, capsys):
    schema_file = tmp_path / "s.json"
    schema_file.write_text(json.dumps({
        "name": "s",
        "fields": [{"name": "x", "type": "string", "required": True}]
    }))
    ns = _parse(["embed", str(schema_file), "--json"])
    rc = handle_embed(ns)
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["schema"] == "s"
    assert len(data["vectors"]) == 1


def test_handle_embed_missing_field_returns_two(tmp_path):
    schema_file = tmp_path / "s.json"
    schema_file.write_text(json.dumps({"name": "s", "fields": []}))
    ns = _parse(["embed", str(schema_file), "--field", "ghost"])
    assert handle_embed(ns) == 2
