"""Compute and compare schema digests (fingerprints) for change detection."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Optional

from streamdiff.schema import StreamSchema


def _schema_to_canonical(schema: StreamSchema) -> dict:
    """Return a stable, sorted dict representation of a schema."""
    fields = [
        {
            "name": f.name,
            "type": f.field_type.value,
            "required": f.required,
        }
        for f in sorted(schema.fields, key=lambda x: x.name)
    ]
    return {"name": schema.name, "fields": fields}


def compute_digest(schema: StreamSchema, algorithm: str = "sha256") -> str:
    """Return a hex digest fingerprint of the schema."""
    canonical = json.dumps(_schema_to_canonical(schema), sort_keys=True)
    h = hashlib.new(algorithm)
    h.update(canonical.encode())
    return h.hexdigest()


@dataclass
class DigestComparison:
    old_digest: str
    new_digest: str
    changed: bool

    def __str__(self) -> str:
        status = "CHANGED" if self.changed else "UNCHANGED"
        return f"[{status}] {self.old_digest[:12]} -> {self.new_digest[:12]}"

    def to_dict(self) -> dict:
        return {
            "old_digest": self.old_digest,
            "new_digest": self.new_digest,
            "changed": self.changed,
        }


def compare_digests(
    old: StreamSchema,
    new: StreamSchema,
    algorithm: str = "sha256",
) -> DigestComparison:
    """Compare two schemas by digest."""
    old_digest = compute_digest(old, algorithm)
    new_digest = compute_digest(new, algorithm)
    return DigestComparison(
        old_digest=old_digest,
        new_digest=new_digest,
        changed=old_digest != new_digest,
    )
