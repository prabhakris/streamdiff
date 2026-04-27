"""Tests for streamdiff.linker."""
import pytest

from streamdiff.schema import FieldType, SchemaField, StreamSchema
from streamdiff.linker import FieldLink, LinkReport, link_schemas


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


# ---------------------------------------------------------------------------
# link_schemas
# ---------------------------------------------------------------------------

def test_link_identical_schemas_all_exact():
    s = _schema(_field("id"), _field("name"))
    report = link_schemas(s, s)
    assert len(report.links) == 2
    assert all(lk.exact for lk in report.links)
    assert report.unlinked_left == []
    assert report.unlinked_right == []


def test_link_disjoint_schemas_no_links():
    left = _schema(_field("a"))
    right = _schema(_field("b"))
    report = link_schemas(left, right)
    assert report.links == []
    assert len(report.unlinked_left) == 1
    assert len(report.unlinked_right) == 1


def test_link_partial_overlap():
    left = _schema(_field("a"), _field("b"))
    right = _schema(_field("b"), _field("c"))
    report = link_schemas(left, right)
    assert len(report.links) == 1
    assert report.links[0].left.name == "b"
    assert len(report.unlinked_left) == 1   # "a"
    assert len(report.unlinked_right) == 1  # "c"


def test_link_type_mismatch_is_not_exact():
    left = _schema(_field("score", FieldType.INT))
    right = _schema(_field("score", FieldType.FLOAT))
    report = link_schemas(left, right)
    assert len(report.links) == 1
    assert report.links[0].exact is False


def test_link_same_name_same_type_is_exact():
    left = _schema(_field("ts", FieldType.LONG))
    right = _schema(_field("ts", FieldType.LONG))
    report = link_schemas(left, right)
    assert report.links[0].exact is True


def test_bool_true_when_links_exist():
    s = _schema(_field("x"))
    report = link_schemas(s, s)
    assert bool(report) is True


def test_bool_false_when_no_links():
    left = _schema(_field("a"))
    right = _schema(_field("b"))
    report = link_schemas(left, right)
    assert bool(report) is False


def test_to_dict_structure():
    s = _schema(_field("id"))
    report = link_schemas(s, s)
    d = report.to_dict()
    assert "links" in d
    assert "unlinked_left" in d
    assert "unlinked_right" in d
    assert d["links"][0]["exact"] is True


def test_field_link_str_exact():
    lf = _field("id", FieldType.STRING)
    rf = _field("id", FieldType.STRING)
    lk = FieldLink(left=lf, right=rf, exact=True)
    assert "exact" in str(lk)
    assert "id" in str(lk)


def test_field_link_str_fuzzy():
    lf = _field("count", FieldType.INT)
    rf = _field("count", FieldType.FLOAT)
    lk = FieldLink(left=lf, right=rf, exact=False)
    assert "fuzzy" in str(lk)
