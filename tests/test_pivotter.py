import pytest
from streamdiff.schema import StreamSchema, SchemaField, FieldType
from streamdiff.pivotter import (
    PivotCell,
    PivotRow,
    PivotResult,
    _extract_dimension,
    pivot_schema,
)


def _field(name: str, ftype: FieldType = FieldType.STRING, required: bool = True) -> SchemaField:
    return SchemaField(name=name, field_type=ftype, required=required)


def _schema(*fields: SchemaField) -> StreamSchema:
    return StreamSchema(name="test", fields=list(fields))


# --- _extract_dimension ---

def test_extract_dimension_with_dot():
    assert _extract_dimension("user.id") == "user"


def test_extract_dimension_no_dot():
    assert _extract_dimension("status") == "__root__"


def test_extract_dimension_custom_separator():
    assert _extract_dimension("order_total", separator="_") == "order"


def test_extract_dimension_nested_only_first_split():
    assert _extract_dimension("a.b.c") == "a"


# --- pivot_schema ---

def test_pivot_empty_schema_returns_empty():
    result = pivot_schema(_schema())
    assert not result
    assert result.rows == []


def test_pivot_flat_fields_all_in_root():
    schema = _schema(_field("id"), _field("name"))
    result = pivot_schema(schema)
    assert len(result.rows) == 1
    assert result.rows[0].dimension == "__root__"
    assert len(result.rows[0].cells) == 2


def test_pivot_groups_by_prefix():
    schema = _schema(
        _field("user.id"),
        _field("user.name"),
        _field("order.id"),
    )
    result = pivot_schema(schema)
    dims = [r.dimension for r in result.rows]
    assert "user" in dims
    assert "order" in dims


def test_pivot_user_group_has_two_cells():
    schema = _schema(_field("user.id"), _field("user.email"), _field("order.total"))
    result = pivot_schema(schema)
    user_row = next(r for r in result.rows if r.dimension == "user")
    assert len(user_row.cells) == 2


def test_pivot_rows_sorted_alphabetically():
    schema = _schema(_field("z.field"), _field("a.field"), _field("m.field"))
    result = pivot_schema(schema)
    dims = [r.dimension for r in result.rows]
    assert dims == sorted(dims)


def test_pivot_cell_attributes():
    schema = _schema(_field("meta.version", FieldType.INTEGER, required=False))
    result = pivot_schema(schema)
    cell = result.rows[0].cells[0]
    assert cell.field_name == "meta.version"
    assert cell.field_type == FieldType.INTEGER.value
    assert cell.required is False


def test_pivot_to_dict_structure():
    schema = _schema(_field("x.y"))
    d = pivot_schema(schema).to_dict()
    assert "rows" in d
    assert "dimension_key" in d
    assert d["rows"][0]["dimension"] == "x"


def test_pivot_str_non_empty():
    schema = _schema(_field("a.b"))
    s = str(pivot_schema(schema))
    assert "Pivot by" in s
    assert "a" in s


def test_pivot_str_empty():
    s = str(pivot_schema(_schema()))
    assert "empty" in s
