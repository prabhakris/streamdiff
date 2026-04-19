from dataclasses import dataclass
from typing import List, Optional
from streamdiff.schema import StreamSchema, SchemaField


@dataclass
class SortResult:
    schema_name: str
    fields: List[SchemaField]
    key: str

    def to_dict(self):
        return {
            "schema": self.schema_name,
            "key": self.key,
            "fields": [
                {"name": f.name, "type": f.field_type.value, "required": f.required}
                for f in self.fields
            ],
        }

    def __str__(self):
        lines = [f"Schema: {self.schema_name} (sorted by {self.key})"]
        for f in self.fields:
            req = "required" if f.required else "optional"
            lines.append(f"  {f.name}: {f.field_type.value} ({req})")
        return "\n".join(lines)


def sort_fields(
    schema: StreamSchema,
    key: str = "name",
    reverse: bool = False,
) -> SortResult:
    """Sort schema fields by a given key.

    Supported keys: 'name', 'type', 'required'
    """
    fields = list(schema.fields)

    if key == "name":
        sorted_fields = sorted(fields, key=lambda f: f.name, reverse=reverse)
    elif key == "type":
        sorted_fields = sorted(fields, key=lambda f: f.field_type.value, reverse=reverse)
    elif key == "required":
        # required=True sorts before optional when reverse=False
        sorted_fields = sorted(fields, key=lambda f: (not f.required, f.name), reverse=reverse)
    else:
        raise ValueError(f"Unsupported sort key: {key!r}. Choose from 'name', 'type', 'required'.")

    return SortResult(schema_name=schema.name, fields=sorted_fields, key=key)
