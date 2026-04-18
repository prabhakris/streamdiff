import pytest
from streamdiff.schema import SchemaField, FieldType
from streamdiff.diff import DiffResult, SchemaChange, ChangeType
from streamdiff.planner import build_plan, MigrationPlan


def _field(name, ftype=FieldType.STRING, required=False):
    return SchemaField(name=name, field_type=ftype, required=required)


def _change(field, ctype, breaking=False, old_field=None):
    return SchemaChange(field=field, change_type=ctype, breaking=breaking, old_field=old_field)


def _result(*changes):
    return DiffResult(changes=list(changes))


def test_no_changes_returns_empty_plan():
    plan = build_plan(_result())
    assert isinstance(plan, MigrationPlan)
    assert plan.steps == []
    assert not plan.has_breaking


def test_added_optional_field_step():
    c = _change(_field("email"), ChangeType.ADDED, breaking=False)
    plan = build_plan(_result(c))
    assert len(plan.steps) == 1
    step = plan.steps[0]
    assert step.action == "ADD_FIELD"
    assert step.field_name == "email"
    assert not step.breaking
    assert "optional" in step.detail


def test_added_required_field_step():
    c = _change(_field("id", required=True), ChangeType.ADDED, breaking=True)
    plan = build_plan(_result(c))
    step = plan.steps[0]
    assert step.breaking
    assert "required" in step.detail


def test_removed_field_step():
    c = _change(_field("old"), ChangeType.REMOVED, breaking=True)
    plan = build_plan(_result(c))
    step = plan.steps[0]
    assert step.action == "DROP_FIELD"
    assert step.breaking


def test_type_changed_step():
    old = _field("count", FieldType.INT)
    new = _field("count", FieldType.STRING)
    c = _change(new, ChangeType.TYPE_CHANGED, breaking=True, old_field=old)
    plan = build_plan(_result(c))
    step = plan.steps[0]
    assert step.action == "ALTER_TYPE"
    assert "int" in step.detail
    assert "string" in step.detail


def test_ordering_type_change_before_add():
    add_c = _change(_field("x"), ChangeType.ADDED)
    old = _field("y", FieldType.INT)
    type_c = _change(_field("y", FieldType.STRING), ChangeType.TYPE_CHANGED, breaking=True, old_field=old)
    plan = build_plan(_result(add_c, type_c))
    assert plan.steps[0].action == "ALTER_TYPE"
    assert plan.steps[1].action == "ADD_FIELD"


def test_has_breaking_true_when_any_breaking():
    c = _change(_field("z"), ChangeType.REMOVED, breaking=True)
    plan = build_plan(_result(c))
    assert plan.has_breaking


def test_to_dict_structure():
    c = _change(_field("a"), ChangeType.ADDED)
    plan = build_plan(_result(c))
    d = plan.to_dict()
    assert "steps" in d
    assert "has_breaking" in d
    assert d["steps"][0]["field"] == "a"
