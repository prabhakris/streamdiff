import pytest
from streamdiff.diff import SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType
from streamdiff.classifier import (
    classify_all,
    group_by_category,
    category_summary,
    CATEGORY_ADDITIVE,
    CATEGORY_DESTRUCTIVE,
    CATEGORY_STRUCTURAL,
    ClassifiedChange,
)


def _field(name: str, required: bool = False, ftype: FieldType = FieldType.STRING) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _change(change_type: ChangeType, name: str = "f", old=None, new=None) -> SchemaChange:
    return SchemaChange(change_type=change_type, field_name=name, old_field=old, new_field=new)


def test_added_is_additive():
    c = _change(ChangeType.ADDED, new=_field("x"))
    result = classify_all([c])
    assert result[0].category == CATEGORY_ADDITIVE


def test_removed_is_destructive():
    c = _change(ChangeType.REMOVED, old=_field("x"))
    result = classify_all([c])
    assert result[0].category == CATEGORY_DESTRUCTIVE


def test_type_changed_is_structural():
    c = _change(ChangeType.TYPE_CHANGED, old=_field("x", ftype=FieldType.INT), new=_field("x", ftype=FieldType.STRING))
    result = classify_all([c])
    assert result[0].category == CATEGORY_STRUCTURAL


def test_required_changed_optional_to_required_is_destructive():
    old = _field("x", required=False)
    new = _field("x", required=True)
    c = _change(ChangeType.REQUIRED_CHANGED, old=old, new=new)
    result = classify_all([c])
    assert result[0].category == CATEGORY_DESTRUCTIVE


def test_required_changed_required_to_optional_is_additive():
    old = _field("x", required=True)
    new = _field("x", required=False)
    c = _change(ChangeType.REQUIRED_CHANGED, old=old, new=new)
    result = classify_all([c])
    assert result[0].category == CATEGORY_ADDITIVE


def test_group_by_category():
    changes = [
        _change(ChangeType.ADDED, name="a", new=_field("a")),
        _change(ChangeType.REMOVED, name="b", old=_field("b")),
        _change(ChangeType.ADDED, name="c", new=_field("c")),
    ]
    classified = classify_all(changes)
    groups = group_by_category(classified)
    assert len(groups[CATEGORY_ADDITIVE]) == 2
    assert len(groups[CATEGORY_DESTRUCTIVE]) == 1


def test_category_summary():
    changes = [
        _change(ChangeType.ADDED, name="a", new=_field("a")),
        _change(ChangeType.REMOVED, name="b", old=_field("b")),
    ]
    classified = classify_all(changes)
    summary = category_summary(classified)
    assert summary[CATEGORY_ADDITIVE] == 1
    assert summary[CATEGORY_DESTRUCTIVE] == 1


def test_to_dict():
    c = _change(ChangeType.ADDED, name="x", new=_field("x"))
    cc = classify_all([c])[0]
    d = cc.to_dict()
    assert d["field"] == "x"
    assert d["category"] == CATEGORY_ADDITIVE
