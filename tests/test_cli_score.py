import argparse
import pytest
from streamdiff.cli_score import add_score_args, apply_score, handle_score_output, score_exit_code
from streamdiff.diff import SchemaChange, ChangeType, DiffResult
from streamdiff.schema import SchemaField, FieldType


def _field(name="x", required=False):
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(ct=ChangeType.ADDED, required=False):
    return SchemaChange(field=_field(required=required), change_type=ct)


def _parse(*args):
    p = argparse.ArgumentParser()
    add_score_args(p)
    return p.parse_args(list(args))


def test_add_score_args_default_false():
    args = _parse()
    assert args.score is False
    assert args.score_threshold is None


def test_add_score_args_flag():
    args = _parse("--score")
    assert args.score is True


def test_add_score_args_threshold():
    args = _parse("--score-threshold", "40")
    assert args.score_threshold == 40


def test_apply_score_no_changes():
    args = _parse()
    result = DiffResult(changes=[])
    risk = apply_score(args, result)
    assert risk.score == 0


def test_apply_score_with_changes():
    args = _parse()
    result = DiffResult(changes=[_change(ChangeType.REMOVED, required=True)])
    risk = apply_score(args, result)
    assert risk.score == 100


def test_score_exit_code_below_threshold():
    args = _parse("--score-threshold", "50")
    result = DiffResult(changes=[_change(ChangeType.ADDED)])
    risk = apply_score(args, result)
    assert score_exit_code(args, risk) == 0


def test_score_exit_code_above_threshold():
    args = _parse("--score-threshold", "10")
    result = DiffResult(changes=[_change(ChangeType.REMOVED, required=True)])
    risk = apply_score(args, result)
    assert score_exit_code(args, risk) == 2


def test_handle_score_output_prints(capsys):
    args = _parse("--score")
    result = DiffResult(changes=[])
    risk = apply_score(args, result)
    handle_score_output(args, risk)
    out = capsys.readouterr().out
    assert "none" in out
