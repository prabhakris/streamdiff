"""shaper.py — reshape a schema by applying field transformations."""
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from streamdiff.schema import SchemaField, StreamSchema


@dataclass
class ShapeResult:
    original: StreamSchema
    shaped: StreamSchema
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return len(self.applied) > 0

    def to_dict(self) -> dict:
        return {
            "original_count": len(self.original.fields),
            "shaped_count": len(self.shaped.fields),
            "applied": self.applied,
            "skipped": self.skipped,
        }

    def __str__(self) -> str:
        return (
            f"ShapeResult(applied={len(self.applied)}, "
            f"skipped={len(self.skipped)})"
        )


Transform = Callable[[SchemaField], Optional[SchemaField]]

_TRANSFORMS: Dict[str, Transform] = {}


def register_transform(name: str, fn: Transform) -> None:
    _TRANSFORMS[name] = fn


def get_transform(name: str) -> Optional[Transform]:
    return _TRANSFORMS.get(name)


def list_transforms() -> List[str]:
    return list(_TRANSFORMS.keys())


def shape_schema(
    schema: StreamSchema,
    transforms: List[str],
) -> ShapeResult:
    """Apply named transforms to each field in order."""
    fns: List[Transform] = []
    skipped_transforms: List[str] = []
    for name in transforms:
        fn = get_transform(name)
        if fn is None:
            skipped_transforms.append(name)
        else:
            fns.append(fn)

    new_fields: List[SchemaField] = []
    applied_names: List[str] = []

    for f in schema.fields:
        result = f
        changed = False
        for fn in fns:
            out = fn(result)
            if out is not None and out != result:
                changed = True
                result = out
        if changed:
            applied_names.append(result.name)
        new_fields.append(result)

    shaped = StreamSchema(name=schema.name, fields=new_fields)
    return ShapeResult(
        original=schema,
        shaped=shaped,
        applied=applied_names,
        skipped=skipped_transforms,
    )


# Built-in transforms
register_transform(
    "require_all",
    lambda f: SchemaField(name=f.name, field_type=f.field_type, required=True)
    if not f.required else None,
)
register_transform(
    "optional_all",
    lambda f: SchemaField(name=f.name, field_type=f.field_type, required=False)
    if f.required else None,
)
