import argparse
import pytest
from streamdiff.diff import SchemaChange, ChangeType, DiffResult
from streamdiff.schema import SchemaField, FieldType
from streamdiff.cli_label import add_label_args, apply_labeling


def _field(name="f", required=False):
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(change_type, name="f", old=None, new=None):
    return SchemaChange(field_name=name, change_type=change_type, old_field=old, new_field=new)


def _parse(args):
    parser = argparse.ArgumentParser()
    add_label_args(parser)
    return parser.parse_args(args)


def _result(changes=None):
    return DiffResult(changes=changes or [])


def test_add_label_args_defaults():
    ns = _parse([])
    assert ns.label is False
    assert ns.label_json is False
    assert ns.extra_labels is None


def test_add_label_args_label_flag():
    ns = _parse(["--label"])
    assert ns.label is True


def test_add_label_args_json_flag():
    ns = _parse(["--label-json"])
    assert ns.label_json is True


def test_add_label_args_extra_labels():
    ns = _parse(["--extra-labels", "reviewed", "approved"])
    assert ns.extra_labels == ["reviewed", "approved"]


def test_apply_labeling_no_flag_does_nothing(capsys):
    ns = _parse([])
    apply_labeling(ns, _result())
    captured = capsys.readouterr()
    assert captured.out == ""


def test_apply_labeling_no_changes_prints_message(capsys):
    ns = _parse(["--label"])
    apply_labeling(ns, _result())
    captured = capsys.readouterr()
    assert "No changes" in captured.out


def test_apply_labeling_shows_labeled_changes(capsys):
    ns = _parse(["--label"])
    c = _change(ChangeType.ADDED, name="new_field", new=_field("new_field"))
    apply_labeling(ns, _result([c]))
    captured = capsys.readouterr()
    assert "new_field" in captured.out
    assert "additive" in captured.out


def test_apply_labeling_json_output(capsys):
    import json
    ns = _parse(["--label-json"])
    c = _change(ChangeType.REMOVED, name="old_field", old=_field("old_field"))
    apply_labeling(ns, _result([c]))
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "labeled_changes" in data
    assert data["labeled_changes"][0]["field"] == "old_field"


def test_apply_labeling_extra_labels_attached(capsys):
    ns = _parse(["--label", "--extra-labels", "ci"])
    c = _change(ChangeType.ADDED, name="x", new=_field("x"))
    apply_labeling(ns, _result([c]))
    captured = capsys.readouterr()
    assert "ci" in captured.out
