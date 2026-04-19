"""Tests for streamdiff.deduplicator."""
import pytest

from streamdiff.diff import ChangeType, DiffResult, SchemaChange
from streamdiff.schema import FieldType, SchemaField
from streamdiff.deduplicator import (
    DeduplicateResult,
    deduplicate,
    deduplicate_into_result,
)


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(name: str, change_type: ChangeType = ChangeType.ADDED) -> SchemaChange:
    return SchemaChange(field_name=name, change_type=change_type, field=_field(name))


def _result(*changes: SchemaChange) -> DiffResult:
    return DiffResult(changes=list(changes))


def test_no_changes_returns_empty_dedup():
    result = deduplicate(_result())
    assert result.kept == []
    assert result.removed == []
    assert not result


def test_unique_changes_all_kept():
    c1 = _change("a", ChangeType.ADDED)
    c2 = _change("b", ChangeType.REMOVED)
    result = deduplicate(_result(c1, c2))
    assert len(result.kept) == 2
    assert len(result.removed) == 0
    assert not result


def test_duplicate_same_field_and_type_removed():
    c1 = _change("a", ChangeType.ADDED)
    c2 = _change("a", ChangeType.ADDED)
    result = deduplicate(_result(c1, c2))
    assert len(result.kept) == 1
    assert len(result.removed) == 1
    assert result


def test_same_field_different_type_both_kept():
    c1 = _change("a", ChangeType.ADDED)
    c2 = _change("a", ChangeType.REMOVED)
    result = deduplicate(_result(c1, c2))
    assert len(result.kept) == 2
    assert len(result.removed) == 0


def test_multiple_duplicates_only_first_kept():
    changes = [_change("x", ChangeType.ADDED) for _ in range(4)]
    result = deduplicate(_result(*changes))
    assert len(result.kept) == 1
    assert len(result.removed) == 3


def test_to_dict_structure():
    c1 = _change("a", ChangeType.ADDED)
    result = deduplicate(_result(c1))
    d = result.to_dict()
    assert d["kept"] == 1
    assert d["removed"] == 0
    assert isinstance(d["changes"], list)


def test_str_no_duplicates():
    result = DeduplicateResult(kept=[], removed=[])
    assert "No duplicates" in str(result)


def test_str_with_duplicates():
    c = _change("a")
    result = DeduplicateResult(kept=[c], removed=[c])
    assert "1 duplicate" in str(result)


def test_deduplicate_into_result_returns_diff_result():
    c1 = _change("a", ChangeType.ADDED)
    c2 = _change("a", ChangeType.ADDED)
    new_result = deduplicate_into_result(_result(c1, c2))
    assert isinstance(new_result, DiffResult)
    assert len(new_result.changes) == 1
