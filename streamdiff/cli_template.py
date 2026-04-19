"""CLI subcommand for schema template operations."""
import argparse
import json
from streamdiff.loader import load_schema
from streamdiff.templater import list_templates, get_template, match_template, apply_template


def add_template_subparser(subparsers) -> None:
    p = subparsers.add_parser("template", help="Apply or check schema templates")
    p.add_argument("schema", help="Path to schema JSON file")
    p.add_argument(
        "--template", required=True, choices=list_templates(), help="Template name to use"
    )
    p.add_argument(
        "--check",
        action="store_true",
        default=False,
        help="Only report missing fields, do not apply",
    )
    p.add_argument(
        "--json", dest="as_json", action="store_true", default=False, help="Output as JSON"
    )
    p.set_defaults(func=handle_template)


def handle_template(args) -> int:
    try:
        schema = load_schema(args.schema)
    except Exception as exc:
        print(f"error: {exc}")
        return 2

    template = get_template(args.template)
    if template is None:
        print(f"error: unknown template '{args.template}'")
        return 2

    missing = match_template(schema, template)

    if args.check:
        if args.as_json:
            print(json.dumps({"template": args.template, "missing": missing}))
        else:
            if missing:
                print(f"Missing required fields for template '{args.template}':")
                for name in missing:
                    print(f"  - {name}")
            else:
                print(f"Schema satisfies template '{args.template}'.")
        return 1 if missing else 0

    result = apply_template(schema, template)
    if args.as_json:
        print(json.dumps({"fields": [{"name": f.name, "type": f.type.value, "required": f.required} for f in result.fields]}))
    else:
        print(f"Applied template '{args.template}'. Fields ({len(result.fields)}):")
        for f in result.fields:
            req = "required" if f.required else "optional"
            print(f"  {f.name} ({f.type.value}, {req})")
    return 0
