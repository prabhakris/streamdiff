import pytest
from streamdiff.diff import SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType
from streamdiff.tagger import (
    tag_change, tag_all, filter_by_tag, tags_summary, TaggedChange
)


def _field(name="age", ftype=FieldType.INT, required=True):
    return SchemaField(name=name, field_type=ftype, required=required)


def _change(name="age", change_type=ChangeType.ADDED, before=None, after=None):
    f = _field(name)
    return SchemaChange(
        field_name=name,
        change_type=change_type,
        before=before or f,
        after=after or f,
    )


def test_added_gets_additive_tag():
    c = _change(change_type=ChangeType.ADDED)
    tc = tag_change(c)
    assert "additive" in tc.tags


def test_removed_gets_destructive_tag():
    c = _change(change_type=ChangeType.REMOVED)
    tc = tag_change(c)
    assert "destructive" in tc.tags


def test_type_changed_gets_destructive_tag():
    c = _change(change_type=ChangeType.TYPE_CHANGED)
    tc = tag_change(c)
    assert "destructive" in tc.tags


def test_required_changed_gets_compatibility_tag():
    c = _change(change_type=ChangeType.REQUIRED_CHANGED)
    tc = tag_change(c)
    assert "compatibility" in tc.tags


def test_extra_tags_applied_to_matching_field():
    c = _change(name="email", change_type=ChangeType.ADDED)
    tc = tag_change(c, extra_tags={"email": ["pii"]})
    assert "pii" in tc.tags
    assert "additive" in tc.tags


def test_extra_tags_not_applied_to_other_fields():
    c = _change(name="age", change_type=ChangeType.ADDED)
    tc = tag_change(c, extra_tags={"email": ["pii"]})
    assert "pii" not in tc.tags


def test_tag_all_returns_tagged_changes():
    changes = [_change("a", ChangeType.ADDED), _change("b", ChangeType.REMOVED)]
    result = tag_all(changes)
    assert len(result) == 2
    assert all(isinstance(r, TaggedChange) for r in result)


def test_filter_by_tag_returns_matching():
    changes = [_change("a", ChangeType.ADDED), _change("b", ChangeType.REMOVED)]
    tagged = tag_all(changes)
    destructive = filter_by_tag(tagged, "destructive")
    assert len(destructive) == 1
    assert destructive[0].change.field_name == "b"


def test_filter_by_tag_returns_empty_when_no_match():
    changes = [_change("a", ChangeType.ADDED), _change("b", ChangeType.ADDED)]
    tagged = tag_all(changes)
    destructive = filter_by_tag(tagged, "destructive")
    assert destructive == []


def test_tags_summary_counts_correctly():
    changes = [
        _change("a", ChangeType.ADDED),
        _change("b", ChangeType.ADDED),
        _change("c", ChangeType.REMOVED),
    ]
    tagged = tag_all(changes)
    summary = tags_summary(tagged)
    assert summary["additive"] == 2
    assert summary["destructive"] == 1


def test_tags_summary_empty_input():
    summary = tags_summary([])
    assert summary == {}


def test_str_representation():
    c = _change("name", ChangeType.ADDED)
    tc = tag_change(c)
    assert "name" in str(tc)
    assert "additive" in str(tc)
