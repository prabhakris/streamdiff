"""Tests for streamdiff.capper."""
from __future__ import annotations

import pytest

from streamdiff.schema import FieldType, SchemaField
from streamdiff.diff import ChangeType, SchemaChange, DiffResult
from streamdiff.capper import cap_by_type, cap_result, CapResult


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(name: str, change_type: ChangeType) -> SchemaChange:
    return SchemaChange(
        field_name=name,
        change_type=change_type,
        old_field=_field(name),
        new_field=_field(name),
    )


def _result(changes: list) -> DiffResult:
    return DiffResult(changes=changes)


def test_no_changes_returns_empty_cap():
    result = cap_by_type([], limits={})
    assert result.kept == []
    assert result.dropped == []


def test_no_limit_keeps_all():
    changes = [
        _change("a", ChangeType.ADDED),
        _change("b", ChangeType.ADDED),
        _change("c", ChangeType.ADDED),
    ]
    result = cap_by_type(changes, limits={}, default_limit=0)
    assert len(result.kept) == 3
    assert result.dropped == []


def test_cap_limits_by_type():
    changes = [
        _change("a", ChangeType.ADDED),
        _change("b", ChangeType.ADDED),
        _change("c", ChangeType.ADDED),
    ]
    result = cap_by_type(changes, limits={ChangeType.ADDED: 2})
    assert len(result.kept) == 2
    assert len(result.dropped) == 1
    assert result.dropped[0].field_name == "c"


def test_cap_does_not_affect_other_types():
    changes = [
        _change("a", ChangeType.ADDED),
        _change("b", ChangeType.REMOVED),
        _change("c", ChangeType.ADDED),
    ]
    result = cap_by_type(changes, limits={ChangeType.ADDED: 1})
    kept_names = {c.field_name for c in result.kept}
    assert "b" in kept_names  # REMOVED is uncapped
    assert len(result.dropped) == 1


def test_cap_result_wraps_diff_result():
    changes = [
        _change("x", ChangeType.TYPE_CHANGED),
        _change("y", ChangeType.TYPE_CHANGED),
    ]
    diff = _result(changes)
    result = cap_result(diff, limits={ChangeType.TYPE_CHANGED: 1})
    assert len(result.kept) == 1
    assert len(result.dropped) == 1


def test_bool_true_when_kept():
    changes = [_change("a", ChangeType.ADDED)]
    result = cap_by_type(changes, limits={})
    assert bool(result) is True


def test_bool_false_when_empty():
    result = cap_by_type([], limits={})
    assert bool(result) is False


def test_to_dict_keys():
    changes = [_change("a", ChangeType.ADDED)]
    result = cap_by_type(changes, limits={})
    d = result.to_dict()
    assert "kept" in d
    assert "dropped" in d
    assert d["kept_count"] == 1
    assert d["dropped_count"] == 0


def test_str_representation():
    result = CapResult(kept=[], dropped=[])
    assert "CapResult" in str(result)
