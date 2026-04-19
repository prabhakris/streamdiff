import pytest
from streamdiff.scorer2 import score_compatibility, overall_score, CompatibilityScore
from streamdiff.diff import SchemaChange, ChangeType, DiffResult
from streamdiff.schema import SchemaField, FieldType


def _field(name, ftype=FieldType.STRING, required=False):
    return SchemaField(name=name, field_type=ftype, required=required)


def _change(name, ctype, old=None, new=None):
    return SchemaChange(field_name=name, change_type=ctype, old_field=old, new_field=new)


def _result(changes):
    return DiffResult(changes=changes)


def test_no_changes_returns_empty():
    result = _result([])
    scores = score_compatibility(result)
    assert scores == []


def test_overall_score_no_changes_is_zero():
    assert overall_score([]) == 0.0


def test_added_optional_is_low_score():
    f = _field("x", required=False)
    c = _change("x", ChangeType.ADDED, new=f)
    scores = score_compatibility(_result([c]))
    assert len(scores) == 1
    assert scores[0].score == pytest.approx(0.1)


def test_added_required_is_high_score():
    f = _field("x", required=True)
    c = _change("x", ChangeType.ADDED, new=f)
    scores = score_compatibility(_result([c]))
    assert scores[0].score == pytest.approx(0.8)


def test_removed_is_max_score():
    f = _field("x")
    c = _change("x", ChangeType.REMOVED, old=f)
    scores = score_compatibility(_result([c]))
    assert scores[0].score == pytest.approx(1.0)


def test_safe_type_change_is_low_score():
    old = _field("x", FieldType.INT)
    new = _field("x", FieldType.LONG)
    c = _change("x", ChangeType.TYPE_CHANGED, old=old, new=new)
    scores = score_compatibility(_result([c]))
    assert scores[0].score == pytest.approx(0.2)


def test_breaking_type_change_is_high_score():
    old = _field("x", FieldType.LONG)
    new = _field("x", FieldType.INT)
    c = _change("x", ChangeType.TYPE_CHANGED, old=old, new=new)
    scores = score_compatibility(_result([c]))
    assert scores[0].score == pytest.approx(0.9)


def test_overall_score_returns_max():
    scores = [
        CompatibilityScore("a", ChangeType.ADDED, 0.1, "optional"),
        CompatibilityScore("b", ChangeType.REMOVED, 1.0, "removed"),
    ]
    assert overall_score(scores) == pytest.approx(1.0)


def test_to_dict_has_expected_keys():
    f = _field("y")
    c = _change("y", ChangeType.REMOVED, old=f)
    scores = score_compatibility(_result([c]))
    d = scores[0].to_dict()
    assert "field" in d
    assert "score" in d
    assert "reason" in d
