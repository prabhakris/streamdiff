"""Tests for streamdiff.grouper."""
import pytest
from streamdiff.diff import SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType
from streamdiff.grouper import group_by_prefix, group_by_change_type, group_summary


def _field(name: str) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=False)


def _change(name: str, ct: ChangeType = ChangeType.ADDED) -> SchemaChange:
    return SchemaChange(field_name=name, change_type=ct, field=_field(name))


def test_group_by_prefix_flat_names():
    changes = [_change("age"), _change("name")]
    groups = group_by_prefix(changes)
    assert set(groups.keys()) == {"age", "name"}
    assert len(groups["age"]) == 1


def test_group_by_prefix_nested_names():
    changes = [_change("user.name"), _change("user.age"), _change("order.id")]
    groups = group_by_prefix(changes)
    assert set(groups.keys()) == {"user", "order"}
    assert len(groups["user"]) == 2
    assert len(groups["order"]) == 1


def test_group_by_prefix_custom_separator():
    changes = [_change("user/name"), _change("user/age")]
    groups = group_by_prefix(changes, separator="/")
    assert "user" in groups
    assert len(groups["user"]) == 2


def test_group_by_change_type():
    changes = [
        _change("a", ChangeType.ADDED),
        _change("b", ChangeType.REMOVED),
        _change("c", ChangeType.ADDED),
    ]
    groups = group_by_change_type(changes)
    assert len(groups[ChangeType.ADDED.value]) == 2
    assert len(groups[ChangeType.REMOVED.value]) == 1


def test_group_summary():
    changes = [_change("user.name"), _change("user.age"), _change("order.id")]
    groups = group_by_prefix(changes)
    summary = group_summary(groups)
    assert summary["user"] == 2
    assert summary["order"] == 1


def test_empty_changes():
    assert group_by_prefix([]) == {}
    assert group_by_change_type([]) == {}
    assert group_summary({}) == {}
