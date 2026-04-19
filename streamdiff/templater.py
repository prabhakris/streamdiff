"""Schema template generation and matching."""
from dataclasses import dataclass, field
from typing import List, Optional
from streamdiff.schema import StreamSchema, SchemaField, FieldType


@dataclass
class TemplateField:
    name: str
    type: FieldType
    required: bool
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type.value,
            "required": self.required,
            "description": self.description,
        }


@dataclass
class SchemaTemplate:
    name: str
    fields: List[TemplateField] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"name": self.name, "fields": [f.to_dict() for f in self.fields]}


BUILTIN_TEMPLATES: dict = {
    "event": SchemaTemplate(
        name="event",
        fields=[
            TemplateField("event_id", FieldType.STRING, True, "Unique event identifier"),
            TemplateField("event_type", FieldType.STRING, True, "Type of event"),
            TemplateField("timestamp", FieldType.LONG, True, "Unix epoch ms"),
            TemplateField("source", FieldType.STRING, False, "Origin service"),
        ],
    ),
    "audit": SchemaTemplate(
        name="audit",
        fields=[
            TemplateField("actor_id", FieldType.STRING, True, "User or service acting"),
            TemplateField("action", FieldType.STRING, True, "Action performed"),
            TemplateField("resource", FieldType.STRING, True, "Resource affected"),
            TemplateField("timestamp", FieldType.LONG, True, "Unix epoch ms"),
            TemplateField("metadata", FieldType.STRING, False, "Extra context"),
        ],
    ),
}


def list_templates() -> List[str]:
    return list(BUILTIN_TEMPLATES.keys())


def get_template(name: str) -> Optional[SchemaTemplate]:
    return BUILTIN_TEMPLATES.get(name)


def match_template(schema: StreamSchema, template: SchemaTemplate) -> List[str]:
    """Return list of missing required template fields in schema."""
    schema_names = {f.name for f in schema.fields}
    missing = []
    for tf in template.fields:
        if tf.required and tf.name not in schema_names:
            missing.append(tf.name)
    return missing


def apply_template(schema: StreamSchema, template: SchemaTemplate) -> StreamSchema:
    """Return new schema with missing template fields appended."""
    existing = {f.name for f in schema.fields}
    new_fields = list(schema.fields)
    for tf in template.fields:
        if tf.name not in existing:
            new_fields.append(SchemaField(name=tf.name, type=tf.type, required=tf.required))
    return StreamSchema(fields=new_fields)
