"""Load StreamSchema from JSON or YAML files."""

import json
from pathlib import Path

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

from streamdiff.schema import FieldType, SchemaField, StreamSchema


def _parse_field(raw: dict) -> SchemaField:
    return SchemaField(
        name=raw["name"],
        type=FieldType(raw["type"]),
        required=raw.get("required", True),
        nullable=raw.get("nullable", False),
        description=raw.get("description", ""),
    )


def _parse_schema(data: dict) -> StreamSchema:
    fields = [_parse_field(f) for f in data.get("fields", [])]
    return StreamSchema(
        name=data["name"],
        version=data.get("version", "0.0.0"),
        fields=fields,
        metadata=data.get("metadata", {}),
    )


def load_schema(path: str | Path) -> StreamSchema:
    """Load a StreamSchema from a JSON or YAML file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")

    suffix = path.suffix.lower()
    raw_text = path.read_text(encoding="utf-8")

    if suffix == ".json":
        data = json.loads(raw_text)
    elif suffix in (".yaml", ".yml"):
        if not _YAML_AVAILABLE:
            raise ImportError("PyYAML is required to load YAML schemas: pip install pyyaml")
        data = yaml.safe_load(raw_text)
    else:
        raise ValueError(f"Unsupported schema file format: {suffix}")

    return _parse_schema(data)
