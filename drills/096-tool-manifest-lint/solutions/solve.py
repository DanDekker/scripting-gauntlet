#!/usr/bin/env python3
"""Lint a tool manifest: one row per (tool, code), last duplicate key wins."""

import json
import os
import re
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9_]+$")


class Pairs(list):
    """A JSON object kept as its ordered (key, value) pairs, duplicates included."""


def to_object(node):
    """Collapse Pairs into a dict, last occurrence winning, like any JSON parser."""
    if isinstance(node, Pairs):
        out = {}
        for key, value in node:
            out[key] = to_object(value)
        return out
    if isinstance(node, list):
        return [to_object(item) for item in node]
    return node


def load_manifest(path):
    raw = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=Pairs)
    names = [key for key, _ in raw]
    # Only top-level keys exist as tools; a repeat is an error, not a second tool.
    duplicates = sorted({name for name in names if names.count(name) > 1})
    return to_object(raw), duplicates


def lint(name, definition):
    codes = []
    if not NAME_RE.match(name):
        codes.append("bad-name")

    description = definition.get("description")
    if not isinstance(description, str) or not description.strip():
        codes.append("no-description")

    parameters = definition.get("parameters")
    if not isinstance(parameters, dict):
        codes.append("no-parameters")
        return codes

    properties = parameters.get("properties")
    if not isinstance(properties, dict) or not properties:
        codes.append("no-properties")
        properties = properties if isinstance(properties, dict) else {}

    required = parameters.get("required")
    if isinstance(required, list):
        if any(entry not in properties for entry in required):
            codes.append("required-not-declared")
    elif "required" not in parameters and properties:
        codes.append("undeclared-required")
    return codes


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest, duplicates = load_manifest(in_dir / "tools.json")

    errors = []
    for name, definition in manifest.items():
        codes = lint(name, definition if isinstance(definition, dict) else {})
        for code in codes:
            errors.append((name, code))
    for name in duplicates:
        errors.append((name, "duplicate-key"))
    errors.sort()

    rows = ["tool,code"] + [f"{name},{code}" for name, code in errors]
    (out_dir / "errors.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

    invalid = len({name for name, _ in errors})
    summary = {
        "tools": len(manifest),
        "valid_tools": len(manifest) - invalid,
        "invalid_tools": invalid,
        "errors": len(errors),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
