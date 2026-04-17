"""Field-level type compatibility comparator for schema changes."""

from dataclasses import dataclass
from typing import Optional
from streamdiff.schema import FieldType

# Matrix of (from_type, to_type) -> is_compatible
_COMPATIBLE_PROMOTIONS: set[tuple[FieldType, FieldType]] = {
    (FieldType.INT, FieldType.LONG),
    (FieldType.INT, FieldType.FLOAT),
    (FieldType.INT, FieldType.DOUBLE),
    (FieldType.LONG, FieldType.DOUBLE),
    (FieldType.FLOAT, FieldType.DOUBLE),
}


@dataclass
class TypeCompatibility:
    from_type: FieldType
    to_type: FieldType
    compatible: bool
    reason: Optional[str] = None

    def __bool__(self) -> bool:
        return self.compatible


def check_type_compatibility(from_type: FieldType, to_type: FieldType) -> TypeCompatibility:
    """Return whether changing from_type to to_type is a safe (non-breaking) promotion."""
    if from_type == to_type:
        return TypeCompatibility(from_type, to_type, True, "no change")

    if (from_type, to_type) in _COMPATIBLE_PROMOTIONS:
        return TypeCompatibility(
            from_type, to_type, True,
            f"{from_type.value} -> {to_type.value} is a safe widening promotion"
        )

    return TypeCompatibility(
        from_type, to_type, False,
        f"{from_type.value} -> {to_type.value} is not a safe type change"
    )


def compatible_types() -> list[tuple[FieldType, FieldType]]:
    """Return all registered compatible type promotion pairs."""
    return list(_COMPATIBLE_PROMOTIONS)
