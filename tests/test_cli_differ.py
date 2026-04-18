import json
import pytest
from argparse import ArgumentParser
from unittest.mock import patch, MagicMock
from streamdiff.cli_differ import add_differ_args, handle_differ
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.diff import DiffResult
from streamdiff.differ import DifferResult


def _parse(*args):
    p = ArgumentParser()
    add_differ_args(p)
    return p.parse_args(args)


def test_defaults():
    ns = _parse("old.yaml", "new.yaml")
    assert ns.score is False
    assert ns.min_severity is None
    assert ns.include is None
    assert ns.exclude is None
    assert ns.json is False


def test_score_flag():
    ns = _parse("old.yaml", "new.yaml", "--score")
    assert ns.score is True


def test_min_severity_flag():
    ns = _parse("old.yaml", "new.yaml", "--min-severity", "error")
    assert ns.min_severity == "error"


def test_include_exclude():
    ns = _parse("old.yaml", "new.yaml", "--include", "a", "b", "--exclude", "c")
    assert ns.include == ["a", "b"]
    assert ns.exclude == ["c"]


def test_handle_differ_returns_zero_on_no_changes(tmp_path):
    content = "name: s\nfields:\n  - name: a\n    type: string\n    required: false\n"
    old = tmp_path / "old.yaml"
    new = tmp_path / "new.yaml"
    old.write_text(content)
    new.write_text(content)
    ns = _parse(str(old), str(new))
    code = handle_differ(ns)
    assert code == 0


def test_handle_differ_returns_one_on_breaking(tmp_path):
    old_c = "name: s\nfields:\n  - name: a\n    type: string\n    required: true\n"
    new_c = "name: s\nfields: []\n"
    old = tmp_path / "old.yaml"
    new = tmp_path / "new.yaml"
    old.write_text(old_c)
    new.write_text(new_c)
    ns = _parse(str(old), str(new))
    code = handle_differ(ns)
    assert code == 1
