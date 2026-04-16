"""Export diff results to various file formats."""
from __future__ import annotations

import json
import csv
import io
from typing import List

from streamdiff.diff import DiffResult, SchemaChange
from streamdiff.formatter import format_summary_dict


def _change_to_dict(change: SchemaChange) -> dict:
    return {
        "change_type": change.change_type.value,
        "field_name": change.field_name,
        "is_breaking": change.is_breaking,
        "old_field": (
            {"name": change.old_field.name, "type": change.old_field.field_type.value,
             "required": change.old_field.required}
            if change.old_field else None
        ),
        "new_field": (
            {"name": change.new_field.name, "type": change.new_field.field_type.value,
             "required": change.new_field.required}
            if change.new_field else None
        ),
    }


def export_json(result: DiffResult, indent: int = 2) -> str:
    """Serialize a DiffResult to a JSON string."""
    payload = {
        "summary": format_summary_dict(result),
        "changes": [_change_to_dict(c) for c in result.changes],
    }
    return json.dumps(payload, indent=indent)


def export_csv(result: DiffResult) -> str:
    """Serialize a DiffResult to a CSV string."""
    fieldnames = ["change_type", "field_name", "is_breaking", "old_type", "new_type"]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for change in result.changes:
        writer.writerow({
            "change_type": change.change_type.value,
            "field_name": change.field_name,
            "is_breaking": change.is_breaking,
            "old_type": change.old_field.field_type.value if change.old_field else "",
            "new_type": change.new_field.field_type.value if change.new_field else "",
        })
    return buf.getvalue()


def write_export(result: DiffResult, fmt: str, path: str) -> None:
    """Write exported diff to *path* in the given format ('json' or 'csv')."""
    if fmt == "json":
        content = export_json(result)
    elif fmt == "csv":
        content = export_csv(result)
    else:
        raise ValueError(f"Unsupported export format: {fmt!r}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
