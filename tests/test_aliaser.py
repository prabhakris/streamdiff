import pytest
from streamdiff.aliaser import AliasMap, apply_aliases, load_alias_map
from streamdiff.diff import SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType


def _field(name="f", required=False):
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(name, change_type):
    return SchemaChange(field_name=name, change_type=change_type, before=_field(name), after=_field(name))


def test_alias_map_add_and_resolve():
    am = AliasMap()
    am.add("old_name", "new_name")
    assert am.resolve("old_name") == "new_name"
    assert am.resolve("missing") is None


def test_alias_map_reverse():
    am = AliasMap()
    am.add("a", "b")
    assert am.reverse() == {"b": "a"}


def test_apply_aliases_suppresses_matched_pair():
    am = AliasMap()
    am.add("old_field", "new_field")
    changes = [
        _change("old_field", ChangeType.REMOVED),
        _change("new_field", ChangeType.ADDED),
    ]
    result = apply_aliases(changes, am)
    assert result == []


def test_apply_aliases_keeps_unmatched():
    am = AliasMap()
    am.add("old_field", "new_field")
    changes = [
        _change("old_field", ChangeType.REMOVED),
        _change("other_field", ChangeType.ADDED),
    ]
    result = apply_aliases(changes, am)
    assert len(result) == 2


def test_apply_aliases_no_mappings_returns_all():
    am = AliasMap()
    changes = [
        _change("x", ChangeType.REMOVED),
        _change("y", ChangeType.ADDED),
    ]
    result = apply_aliases(changes, am)
    assert len(result) == 2


def test_load_alias_map_from_dict():
    am = load_alias_map({"foo": "bar", "baz": "qux"})
    assert am.resolve("foo") == "bar"
    assert am.resolve("baz") == "qux"


def test_partial_pair_not_suppressed():
    am = AliasMap()
    am.add("old", "new")
    # only removed, no added counterpart
    changes = [_change("old", ChangeType.REMOVED)]
    result = apply_aliases(changes, am)
    assert len(result) == 1
