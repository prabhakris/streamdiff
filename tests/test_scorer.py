import pytest
from streamdiff.scorer import score_changes, score_result, RiskScore
from streamdiff.diff import SchemaChange, ChangeType, DiffResult
from streamdiff.schema import SchemaField, FieldType


def _field(name="f", required=False):
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _change(ct, required=False):
    return SchemaChange(field=_field(required=required), change_type=ct)


def test_no_changes_score_zero():
    r = score_changes([])
    assert r.score == 0
    assert r.label == "none"


def test_added_optional_is_low():
    r = score_changes([_change(ChangeType.ADDED)])
    assert r.score == 5
    assert r.label == "low"


def test_removed_optional_is_medium():
    r = score_changes([_change(ChangeType.REMOVED)])
    assert r.score == 50
    assert r.label == "medium"


def test_removed_required_is_high():
    r = score_changes([_change(ChangeType.REMOVED, required=True)])
    assert r.score == 100
    assert r.label == "high"


def test_type_changed_required_is_high():
    r = score_changes([_change(ChangeType.TYPE_CHANGED, required=True)])
    assert r.score == 60
    assert r.label == "high"


def test_score_capped_at_100():
    changes = [_change(ChangeType.REMOVED, required=True)] * 5
    r = score_changes(changes)
    assert r.score == 100


def test_breakdown_keys_present():
    r = score_changes([_change(ChangeType.ADDED)])
    assert "added" in r.breakdown
    assert "removed" in r.breakdown


def test_score_result_uses_changes():
    result = DiffResult(changes=[_change(ChangeType.ADDED)])
    r = score_result(result)
    assert r.score == 5


def test_str_representation():
    r = RiskScore(score=42, label="medium", breakdown={})
    assert "medium" in str(r)
    assert "42" in str(r)
