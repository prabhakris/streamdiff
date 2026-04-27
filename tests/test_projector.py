"""Tests for streamdiff.projector."""
import pytest

from streamdiff.schema import FieldType, SchemaField, StreamSchema
from streamdiff.projector import ProjectResult, project_schema, _matches_path


def _field(name: str, required: bool = True, ftype: FieldType = FieldType.STRING) -> SchemaField:
    return SchemaField(name=name, type=ftype, required=required)


def _schema(*names: str) -> StreamSchema:
    return StreamSchema(fields=[_field(n) for n in names])


# --- _matches_path ---

def test_matches_path_exact():
    assert _matches_path("user.id", {"user.id"}) is True


def test_matches_path_prefix():
    assert _matches_path("user.address.city", {"user.address"}) is True


def test_matches_path_no_match():
    assert _matches_path("order.id", {"user.id", "user.name"}) is False


def test_matches_path_partial_prefix_not_matched():
    # 'user' should not match 'username'
    assert _matches_path("username", {"user"}) is False


# --- project_schema ---

def test_project_no_paths_returns_all():
    schema = _schema("id", "name", "email")
    result = project_schema(schema, paths=None)
    assert len(result.included) == 3
    assert len(result.excluded) == 0


def test_project_empty_paths_returns_all():
    schema = _schema("id", "name")
    result = project_schema(schema, paths=[])
    assert len(result.included) == 2


def test_project_single_path():
    schema = _schema("id", "name", "email")
    result = project_schema(schema, paths=["id"])
    assert len(result.included) == 1
    assert result.included[0].name == "id"
    assert len(result.excluded) == 2


def test_project_multiple_paths():
    schema = _schema("id", "name", "email", "created_at")
    result = project_schema(schema, paths=["id", "email"])
    included_names = {f.name for f in result.included}
    assert included_names == {"id", "email"}
    assert len(result.excluded) == 2


def test_project_no_match_returns_empty_included():
    schema = _schema("id", "name")
    result = project_schema(schema, paths=["nonexistent"])
    assert len(result.included) == 0
    assert len(result.excluded) == 2


def test_project_bool_true_when_included():
    schema = _schema("id")
    result = project_schema(schema, paths=["id"])
    assert bool(result) is True


def test_project_bool_false_when_empty():
    schema = _schema("id")
    result = project_schema(schema, paths=["missing"])
    assert bool(result) is False


def test_project_to_schema_returns_stream_schema():
    schema = _schema("id", "name", "email")
    result = project_schema(schema, paths=["id", "name"])
    out = result.to_schema()
    assert len(out.fields) == 2
    assert {f.name for f in out.fields} == {"id", "name"}


def test_project_to_dict_keys():
    schema = _schema("a", "b", "c")
    result = project_schema(schema, paths=["a"])
    d = result.to_dict()
    assert "included" in d
    assert "excluded" in d
    assert "paths" in d
    assert d["included_count"] == 1
    assert d["excluded_count"] == 2


def test_project_str_shows_included_fields():
    schema = _schema("id", "name")
    result = project_schema(schema, paths=["id"])
    text = str(result)
    assert "id" in text
    assert "1 included" in text
