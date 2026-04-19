import pytest
from streamdiff.diff import SchemaChange, ChangeType
from streamdiff.schema import SchemaField, FieldType
from streamdiff.labeler import (
    label_change,
    label_all,
    build_label_report,
    LabeledChange,
    LabelReport,
)


def _field(name="f", required=False, ftype=FieldType.STRING):
    return SchemaField(name=name, field_type=ftype, required=required)


def _change(change_type, name="f", old=None, new=None):
    return SchemaChange(field_name=name, change_type=change_type, old_field=old, new_field=new)


def test_added_optional_gets_additive_safe():
    c = _change(ChangeType.ADDED, new=_field(required=False))
    lc = label_change(c)
    assert "additive" in lc.labels
    assert "safe" in lc.labels
    assert "breaking" not in lc.labels


def test_added_required_gets_additive_breaking():
    c = _change(ChangeType.ADDED, new=_field(required=True))
    lc = label_change(c)
    assert "additive" in lc.labels
    assert "breaking" in lc.labels
    assert "safe" not in lc.labels


def test_removed_gets_destructive_breaking():
    c = _change(ChangeType.REMOVED, old=_field())
    lc = label_change(c)
    assert "destructive" in lc.labels
    assert "breaking" in lc.labels


def test_type_changed_gets_structural_breaking():
    c = _change(ChangeType.TYPE_CHANGED, old=_field(), new=_field())
    lc = label_change(c)
    assert "structural" in lc.labels
    assert "breaking" in lc.labels


def test_extra_labels_appended():
    c = _change(ChangeType.ADDED, new=_field())
    lc = label_change(c, extra=["reviewed", "approved"])
    assert "reviewed" in lc.labels
    assert "approved" in lc.labels


def test_label_all_returns_one_per_change():
    changes = [
        _change(ChangeType.ADDED, name="a", new=_field("a")),
        _change(ChangeType.REMOVED, name="b", old=_field("b")),
    ]
    result = label_all(changes)
    assert len(result) == 2


def test_labeled_change_str():
    c = _change(ChangeType.REMOVED, name="x", old=_field("x"))
    lc = label_change(c)
    s = str(lc)
    assert "x" in s
    assert "destructive" in s


def test_labeled_change_to_dict():
    c = _change(ChangeType.ADDED, name="y", new=_field("y"))
    lc = label_change(c)
    d = lc.to_dict()
    assert d["field"] == "y"
    assert isinstance(d["labels"], list)


def test_build_label_report_bool_false_on_empty():
    report = LabelReport(labeled=[])
    assert not report


def test_build_label_report_bool_true_on_changes():
    c = _change(ChangeType.ADDED, new=_field())
    report = build_label_report([c])
    assert report
    assert len(report.labeled) == 1


def test_report_to_dict():
    c = _change(ChangeType.REMOVED, name="z", old=_field("z"))
    report = build_label_report([c])
    d = report.to_dict()
    assert "labeled_changes" in d
    assert d["labeled_changes"][0]["field"] == "z"
