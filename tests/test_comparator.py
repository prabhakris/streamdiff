"""Tests for streamdiff.comparator."""

import pytest
from streamdiff.schema import FieldType
from streamdiff.comparator import check_type_compatibility, compatible_types, TypeCompatibility


def test_same_type_is_compatible():
    result = check_type_compatibility(FieldType.STRING, FieldType.STRING)
    assert result.compatible is True
    assert result.reason == "no change"


def test_int_to_long_is_safe():
    result = check_type_compatibility(FieldType.INT, FieldType.LONG)
    assert result.compatible is True
    assert "safe" in result.reason


def test_int_to_double_is_safe():
    result = check_type_compatibility(FieldType.INT, FieldType.DOUBLE)
    assert result.compatible is True


def test_float_to_double_is_safe():
    result = check_type_compatibility(FieldType.FLOAT, FieldType.DOUBLE)
    assert result.compatible is True


def test_long_to_int_is_breaking():
    result = check_type_compatibility(FieldType.LONG, FieldType.INT)
    assert result.compatible is False
    assert "not a safe" in result.reason


def test_string_to_int_is_breaking():
    result = check_type_compatibility(FieldType.STRING, FieldType.INT)
    assert result.compatible is False


def test_double_to_float_is_breaking():
    result = check_type_compatibility(FieldType.DOUBLE, FieldType.FLOAT)
    assert result.compatible is False


def test_bool_result():
    compat = check_type_compatibility(FieldType.INT, FieldType.LONG)
    assert bool(compat) is True
    incompat = check_type_compatibility(FieldType.LONG, FieldType.INT)
    assert bool(incompat) is False


def test_compatible_types_returns_list():
    pairs = compatible_types()
    assert isinstance(pairs, list)
    assert (FieldType.INT, FieldType.LONG) in pairs
    assert (FieldType.FLOAT, FieldType.DOUBLE) in pairs


def test_type_compatibility_dataclass_fields():
    result = check_type_compatibility(FieldType.INT, FieldType.FLOAT)
    assert result.from_type == FieldType.INT
    assert result.to_type == FieldType.FLOAT
