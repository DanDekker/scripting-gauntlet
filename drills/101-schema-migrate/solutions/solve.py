#!/usr/bin/env python3
"""Diff two JSON schemas at the top level: breaking changes vs additive ones."""

import csv
import json
import os
from pathlib import Path

BREAKING = {"removed", "type-changed", "now-required"}
SAFE = {"added", "now-optional"}


def load(path):
    schema = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(schema, dict):
        raise SystemExit(f"{path}: schema is not a JSON object")
    return schema


def properties(schema):
    props = schema.get("properties") or {}
    if not isinstance(props, dict):
        raise SystemExit("properties is not an object")
    return props


def type_of(definition):
    if not isinstance(definition, dict):
        return ""
    return definition.get("type") or ""


def required_set(schema, props):
    names = schema.get("required") or []
    if not isinstance(names, list):
        raise SystemExit("required is not an array")
    return {name for name in names if isinstance(name, str) and name in props}


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    old, new = load(in_dir / "old_schema.json"), load(in_dir / "new_schema.json")
    old_props, new_props = properties(old), properties(new)
    old_req, new_req = required_set(old, old_props), required_set(new, new_props)

    rows = []
    for name in sorted(set(old_props) | set(new_props)):
        if name not in new_props:
            rows.append((name, "removed"))
            continue
        if name not in old_props:
            rows.append((name, "added"))
            continue
        if type_of(old_props[name]) != type_of(new_props[name]):
            rows.append((name, "type-changed"))
        if name in new_req and name not in old_req:
            rows.append((name, "now-required"))
        if name in old_req and name not in new_req:
            rows.append((name, "now-optional"))

    rows.sort(key=lambda row: (row[0], row[1]))

    with (out_dir / "changes.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["property", "code"])
        writer.writerows(rows)

    summary = {
        "breaking": sum(1 for _, code in rows if code in BREAKING),
        "safe": sum(1 for _, code in rows if code in SAFE),
        "properties": len({name for name, _ in rows}),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
