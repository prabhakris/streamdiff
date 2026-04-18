import json
import argparse
import pytest
from streamdiff.cli_alias import add_alias_args, load_alias_map_from_args, apply_alias_args
from streamdiff.diff import SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType


def _field(name="f"):
    return SchemaField(name=name, field_type=FieldType.STRING, required=False)


def _change(name, change_type):
    return SchemaChange(field_name=name, change_type=change_type, before=_field(name), after=_field(name))


def _parse(args):
    parser = argparse.ArgumentParser()
    add_alias_args(parser)
    return parser.parse_args(args)


def test_add_alias_args_default_none():
    ns = _parse([])
    assert ns.alias_map is None


def test_add_alias_args_accepts_file():
    ns = _parse(["--alias-map", "aliases.json"])
    assert ns.alias_map == "aliases.json"


def test_load_alias_map_none_when_no_arg():
    ns = _parse([])
    result = load_alias_map_from_args(ns)
    assert result is None


def test_load_alias_map_from_file(tmp_path):
    f = tmp_path / "aliases.json"
    f.write_text(json.dumps({"old": "new"}))
    ns = _parse(["--alias-map", str(f)])
    am = load_alias_map_from_args(ns)
    assert am is not None
    assert am.resolve("old") == "new"


def test_apply_alias_args_no_map_returns_all():
    ns = _parse([])
    changes = [_change("x", ChangeType.REMOVED)]
    result = apply_alias_args(changes, ns)
    assert len(result) == 1


def test_apply_alias_args_with_map_suppresses(tmp_path):
    f = tmp_path / "aliases.json"
    f.write_text(json.dumps({"old": "new"}))
    ns = _parse(["--alias-map", str(f)])
    changes = [
        _change("old", ChangeType.REMOVED),
        _change("new", ChangeType.ADDED),
    ]
    result = apply_alias_args(changes, ns)
    assert result == []
