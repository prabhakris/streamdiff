import argparse
import pytest
from streamdiff.cli_annotate import add_annotate_args, apply_annotation, format_annotations
from streamdiff.diff import SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType
from streamdiff.annotator import AnnotatedChange


def _field(name="f", ftype=FieldType.STRING, required=False):
    return SchemaField(name=name, field_type=ftype, required=required)


def _change(change_type=ChangeType.ADDED, old=None, new=None):
    return SchemaChange(change_type=change_type, old_field=old, new_field=new)


def _parse(args):
    parser = argparse.ArgumentParser()
    add_annotate_args(parser)
    return parser.parse_args(args)


def test_add_annotate_args_default_false():
    ns = _parse([])
    assert ns.annotate is False


def test_add_annotate_args_flag_true():
    ns = _parse(["--annotate"])
    assert ns.annotate is True


def test_apply_annotation_returns_none_when_flag_off():
    ns = _parse([])
    changes = [_change(new=_field("x"))]
    result = apply_annotation(ns, changes)
    assert result is None


def test_apply_annotation_returns_list_when_flag_on():
    ns = _parse(["--annotate"])
    changes = [_change(new=_field("x"))]
    result = apply_annotation(ns, changes)
    assert result is not None
    assert len(result) == 1
    assert isinstance(result[0], AnnotatedChange)


def test_format_annotations_empty():
    text = format_annotations([])
    assert "No changes" in text


def test_format_annotations_shows_hint():
    from streamdiff.annotator import annotate
    c = _change(ChangeType.REMOVED, old=_field("gone"))
    annotated = [annotate(c)]
    text = format_annotations(annotated)
    assert "Hint:" in text
    assert "gone" in text


def test_format_annotations_multiple():
    from streamdiff.annotator import annotate_all
    changes = [
        _change(ChangeType.ADDED, new=_field("a")),
        _change(ChangeType.REMOVED, old=_field("b")),
    ]
    text = format_annotations(annotate_all(changes))
    assert "a" in text
    assert "b" in text
