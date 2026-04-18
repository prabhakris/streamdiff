"""CLI support for alias map loading and application."""
import json
import argparse
from typing import Optional
from streamdiff.aliaser import AliasMap, load_alias_map, apply_aliases
from streamdiff.diff import SchemaChange


def add_alias_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--alias-map",
        metavar="FILE",
        default=None,
        help="JSON file mapping old field names to new names (alias pairs to suppress)",
    )


def load_alias_map_from_args(args: argparse.Namespace) -> Optional[AliasMap]:
    path = getattr(args, "alias_map", None)
    if not path:
        return None
    try:
        with open(path) as fh:
            data = json.load(fh)
    except FileNotFoundError:
        raise FileNotFoundError(f"Alias map file not found: {path!r}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Alias map file contains invalid JSON: {path!r}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Alias map file must contain a JSON object, got: {type(data)}")
    return load_alias_map(data)


def apply_alias_args(changes: list[SchemaChange], args: argparse.Namespace) -> list[SchemaChange]:
    alias_map = load_alias_map_from_args(args)
    if alias_map is None:
        return changes
    return apply_aliases(changes, alias_map)
