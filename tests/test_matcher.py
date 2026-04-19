import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.matcher import match_schemas, FieldMatch, MatchReport


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


def test_exact_match_all_fields():
    old = _schema(_field("id"), _field("name"))
    new = _schema(_field("id"), _field("name"))
    report = match_schemas(old, new)
    assert len(report.matches) == 2
    assert all(m.exact for m in report.matches)
    assert not report.unmatched_old
    assert not report.unmatched_new
    assert bool(report)


def test_added_field_is_unmatched_new():
    old = _schema(_field("id"))
    new = _schema(_field("id"), _field("email"))
    report = match_schemas(old, new)
    assert len(report.matches) == 1
    assert [f.name for f in report.unmatched_new] == ["email"]
    assert not report.unmatched_old


def test_removed_field_is_unmatched_old():
    old = _schema(_field("id"), _field("legacy"))
    new = _schema(_field("id"))
    report = match_schemas(old, new)
    assert len(report.unmatched_old) == 1
    assert report.unmatched_old[0].name == "legacy"
    assert not report.unmatched_new


def test_type_changed_is_partial_match():
    old = _schema(_field("count", FieldType.INT))
    new = _schema(_field("count", FieldType.STRING))
    report = match_schemas(old, new)
    assert len(report.matches) == 1
    m = report.matches[0]
    assert m.name_match
    assert not m.type_match
    assert not m.exact


def test_bool_false_when_unmatched():
    old = _schema(_field("a"))
    new = _schema(_field("b"))
    report = match_schemas(old, new)
    assert not bool(report)


def test_to_dict_structure():
    old = _schema(_field("x"))
    new = _schema(_field("x"))
    report = match_schemas(old, new)
    d = report.to_dict()
    assert "matches" in d
    assert "unmatched_old" in d
    assert "unmatched_new" in d
    assert d["matches"][0]["exact"] is True


def test_str_on_match():
    m = FieldMatch(
        old_field=_field("foo"),
        new_field=_field("foo"),
        name_match=True,
        type_match=True,
    )
    assert "foo" in str(m)
    assert "exact" in str(m)
