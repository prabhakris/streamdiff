import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.pinner import (
    save_pin, load_pin, list_pins, delete_pin, compare_to_pin, pin_path
)


def _field(name: str, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=FieldType.STRING, required=required)


def _schema(*names: str) -> StreamSchema:
    return StreamSchema(name="test", fields=[_field(n) for n in names])


@pytest.fixture
def tmp_pins(tmp_path):
    return str(tmp_path / "pins")


def test_save_creates_file(tmp_pins):
    schema = _schema("id", "name")
    path = save_pin("v1", schema, pins_dir=tmp_pins)
    import os
    assert os.path.exists(path)

_returns_none_when_missing(tmp_pins):
    result = load_pin("nonexistent", pins_dir=tmp_pins)
    assert result is None


def test_save_and_load_roundtrip(tmp_pins):
    schema = _schema("id", "email")
    save_pin("v1", schema, pins_dir=tmp_pins)
    loaded = load_pin("v1", pins_dir=tmp_pins)
    assert loaded is not None
    assert {f.name for f in loaded.fields} == {"id", "email"}


def test_list_pins_empty(tmp_pins):
    assert list_pins(pins_dir=tmp_pins) == []


def test_list_pins_shows_saved(tmp_pins):
    save_pin("alpha", _schema("x"), pins_dir=tmp_pins)
    save_pin("beta", _schema("y"), pins_dir=tmp_pins)
    pins = list_pins(pins_dir=tmp_pins)
    assert set(pins) == {"alpha", "beta"}


def test_delete_pin_removes_file(tmp_pins):
    save_pin("v1", _schema("a"), pins_dir=tmp_pins)
    assert delete_pin("v1", pins_dir=tmp_pins) is True
    assert load_pin("v1", pins_dir=tmp_pins) is None


def test_delete_pin_missing_returns_false(tmp_pins):
    assert delete_pin("ghost", pins_dir=tmp_pins) is False


def test_compare_no_pin_not_found(tmp_pins):
    result = compare_to_pin("v1", _schema("id"), pins_dir=tmp_pins)
    assert not result.found
    assert result.diff is None


def test_compare_no_changes(tmp_pins):
    schema = _schema("id", "name")
    save_pin("v1", schema, pins_dir=tmp_pins)
    result = compare_to_pin("v1", schema, pins_dir=tmp_pins)
    assert result.found
    assert result.diff is not None
    assert len(result.diff.changes) == 0


def test_compare_detects_added_field(tmp_pins):
    old = _schema("id")
    new = _schema("id", "email")
    save_pin("v1", old, pins_dir=tmp_pins)
    result = compare_to_pin("v1", new, pins_dir=tmp_pins)
    assert result.found
    assert any(c.field_name == "email" for c in result.diff.changes)
