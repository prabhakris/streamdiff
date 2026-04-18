import json
import pytest
from argparse import ArgumentParser, Namespace
from unittest.mock import patch, MagicMock
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.profiler import ProfileResult, FieldStat
from streamdiff.cli_profile import add_profile_subparser, handle_profile


def _parse(args):
    p = ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_profile_subparser(sub)
    return p.parse_args(args)


def _make_result():
    stats = [FieldStat(name="id", field_type=FieldType.INT, required=True, depth=1)]
    return ProfileResult(
        schema_name="test",
        total_fields=1,
        required_count=1,
        optional_count=0,
        type_counts={"int": 1},
        max_depth=1,
        stats=stats,
    )


def test_add_profile_subparser_defaults():
    ns = _parse(["profile", "schema.json"])
    assert ns.schema == "schema.json"
    assert ns.output_json is False
    assert ns.min_depth == 0


def test_add_profile_subparser_json_flag():
    ns = _parse(["profile", "schema.json", "--json"])
    assert ns.output_json is True


def test_add_profile_subparser_min_depth():
    ns = _parse(["profile", "schema.json", "--min-depth", "2"])
    assert ns.min_depth == 2


def test_handle_profile_text_output(capsys):
    schema = StreamSchema(name="orders", fields=[
        SchemaField(name="id", field_type=FieldType.INT, required=True)
    ])
    args = Namespace(schema="x.json", output_json=False, min_depth=0)
    with patch("streamdiff.cli_profile.load_schema", return_value=schema):
        code = handle_profile(args)
    captured = capsys.readouterr()
    assert code == 0
    assert "orders" in captured.out
    assert "Fields" in captured.out


def test_handle_profile_json_output(capsys):
    schema = StreamSchema(name="orders", fields=[
        SchemaField(name="id", field_type=FieldType.INT, required=True)
    ])
    args = Namespace(schema="x.json", output_json=True, min_depth=0)
    with patch("streamdiff.cli_profile.load_schema", return_value=schema):
        code = handle_profile(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["schema_name"] == "orders"
    assert code == 0


def test_handle_profile_min_depth_filters(capsys):
    schema = StreamSchema(name="s", fields=[
        SchemaField(name="a", field_type=FieldType.STRING, required=True),
        SchemaField(name="a.b", field_type=FieldType.STRING, required=False),
    ])
    args = Namespace(schema="x.json", output_json=False, min_depth=2)
    with patch("streamdiff.cli_profile.load_schema", return_value=schema):
        handle_profile(args)
    captured = capsys.readouterr()
    assert "a.b" in captured.out
    assert "  a (" not in captured.out
