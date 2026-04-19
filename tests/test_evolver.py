import pytest
from streamdiff.schema import SchemaField, FieldType, StreamSchema
from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.evolver import EvolutionSuggestion, EvolutionPlan, build_evolution_plan, _suggest_for_change


def _field(name: str, ftype=FieldType.STRING, required: bool = False) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _change(ctype, name, old=None, new=None) -> SchemaChange:
    return SchemaChange(change_type=ctype, field_name=name, old_field=old, new_field=new)


def _result(*changes) -> DiffResult:
    return DiffResult(changes=list(changes))


def test_no_changes_returns_empty_plan():
    plan = build_evolution_plan(_result())
    assert not plan
    assert plan.suggestions == []


def test_added_optional_suggests_keep():
    c = _change(ChangeType.ADDED, "score", new=_field("score", required=False))
    s = _suggest_for_change(c)
    assert s.action == "keep"
    assert s.field_name == "score"


def test_added_required_suggests_promote():
    c = _change(ChangeType.ADDED, "user_id", new=_field("user_id", required=True))
    s = _suggest_for_change(c)
    assert s.action == "promote"


def test_removed_field_suggests_deprecate():
    c = _change(ChangeType.REMOVED, "legacy", old=_field("legacy"))
    s = _suggest_for_change(c)
    assert s.action == "deprecate"
    assert "deprecat" in s.reason.lower()


def test_type_changed_suggests_deprecate():
    c = _change(ChangeType.TYPE_CHANGED, "amount",
                old=_field("amount", FieldType.INT),
                new=_field("amount", FieldType.STRING))
    s = _suggest_for_change(c)
    assert s.action == "deprecate"
    assert "breaking" in s.reason.lower()


def test_build_plan_multiple_changes():
    changes = [
        _change(ChangeType.ADDED, "x", new=_field("x")),
        _change(ChangeType.REMOVED, "y", old=_field("y")),
    ]
    plan = build_evolution_plan(_result(*changes))
    assert len(plan.suggestions) == 2
    actions = {s.field_name: s.action for s in plan.suggestions}
    assert actions["x"] == "keep"
    assert actions["y"] == "deprecate"


def test_to_dict_structure():
    c = _change(ChangeType.REMOVED, "old_field", old=_field("old_field"))
    plan = build_evolution_plan(_result(c))
    d = plan.to_dict()
    assert "suggestions" in d
    assert d["suggestions"][0]["field"] == "old_field"
    assert d["suggestions"][0]["action"] == "deprecate"


def test_suggestion_str():
    s = EvolutionSuggestion("foo", "keep", "All good.")
    assert "KEEP" in str(s)
    assert "foo" in str(s)
