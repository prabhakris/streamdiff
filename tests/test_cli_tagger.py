import argparse
import pytest
from streamdiff.diff import SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType
from streamdiff.cli_tagger import add_tagger_args, apply_tagging, format_tag_summary


def _field(name="x"):
    return SchemaField(name=name, field_type=FieldType.STRING, required=False)


def _change(name="x", change_type=ChangeType.ADDED):
    f = _field(name)
    return SchemaChange(field_name=name, change_type=change_type, before=f, after=f)


def _parse(args=None):
    parser = argparse.ArgumentParser()
    add_tagger_args(parser)
    return parser.parse_args(args or [])


def test_add_tagger_args_defaults():
    ns = _parse([])
    assert ns.tag_filter is None
    assert ns.tag_field == []
    assert ns.show_tag_summary is False


def test_add_tagger_args_tag_filter():
    ns = _parse(["--tag-filter", "destructive"])
    assert ns.tag_filter == "destructive"


def test_add_tagger_args_tag_field():
    ns = _parse(["--tag-field", "email", "pii"])
    assert ns.tag_field == [["email", "pii"]]


def test_add_tagger_args_show_summary():
    ns = _parse(["--show-tag-summary"])
    assert ns.show_tag_summary is True


def test_apply_tagging_no_filter_returns_all():
    changes = [_change("a", ChangeType.ADDED), _change("b", ChangeType.REMOVED)]
    ns = _parse([])
    tagged = apply_tagging(changes, ns)
    assert len(tagged) == 2


def test_apply_tagging_filter_destructive():
    changes = [_change("a", ChangeType.ADDED), _change("b", ChangeType.REMOVED)]
    ns = _parse(["--tag-filter", "destructive"])
    tagged = apply_tagging(changes, ns)
    assert len(tagged) == 1
    assert tagged[0].change.field_name == "b"


def test_apply_tagging_custom_tag_field():
    changes = [_change("email", ChangeType.ADDED)]
    ns = _parse(["--tag-field", "email", "pii"])
    tagged = apply_tagging(changes, ns)
    assert "pii" in tagged[0].tags


def test_format_tag_summary_no_tags():
    result = format_tag_summary([])
    assert "none" in result


def test_format_tag_summary_with_tags():
    changes = [_change("a", ChangeType.ADDED), _change("b", ChangeType.REMOVED)]
    ns = _parse([])
    tagged = apply_tagging(changes, ns)
    summary = format_tag_summary(tagged)
    assert "additive" in summary
    assert "destructive" in summary
