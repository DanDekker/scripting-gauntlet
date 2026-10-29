#!/usr/bin/env python3
"""Validate the arguments a model put in a tool call against the tool's schema."""

import json
import os
from pathlib import Path

MISSING = object()


def type_ok(value, declared):
    if declared == "string":
        return isinstance(value, str)
    if declared == "integer":
        if isinstance(value, bool):
            return False
        if isinstance(value, int):
            return True
        return isinstance(value, float) and value.is_integer()
    if declared == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if declared == "boolean":
        return isinstance(value, bool)
    if declared == "object":
        return isinstance(value, dict)
    if declared == "array":
        return isinstance(value, list)
    return True


def same_value(left, right):
    """JSON equality: true is not 1."""
    if isinstance(left, bool) != isinstance(right, bool):
        return False
    return left == right


def validate(args, props, required):
    """Return the error list for one validated call, in contract order."""
    errors = []
    for prop in required:
        if prop not in args:
            errors.append("missing:" + prop)
    for prop in args:
        if prop not in props:
            errors.append("unknown:" + prop)
    for prop, value in args.items():
        spec = props.get(prop)
        if spec is None:
            continue
        if value is None and prop not in required:
            continue
        if not type_ok(value, spec.get("type")):
            errors.append("type:" + prop)
    for prop, value in args.items():
        spec = props.get(prop)
        if spec is None:
            continue
        if value is None and prop not in required:
            continue
        if "enum" in spec and type_ok(value, spec.get("type")):
            if not any(same_value(value, option) for option in spec["enum"]):
                errors.append("enum:" + prop)
    for prop, value in args.items():
        spec = props.get(prop)
        if spec is None:
            continue
        if "minimum" in spec and isinstance(value, (int, float)) and not isinstance(value, bool):
            if value < spec["minimum"]:
                errors.append("min:" + prop)
    return errors


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    schema = json.loads((in_dir / "schema.json").read_text(encoding="utf-8"))
    tool = schema["name"]
    props = schema.get("properties") or {}
    required = schema.get("required") or []

    rows = []
    calls = valid = invalid = wrong_tool = bad_arguments = total_errors = 0

    for line in (in_dir / "calls.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            call = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(call, dict):
            continue
        name = call.get("name")
        call_id = call.get("call_id")
        if not isinstance(name, str) or not isinstance(call_id, str):
            continue
        calls += 1
        if name != tool:
            wrong_tool += 1
            valid += 1
            continue
        args = call.get("arguments", MISSING)
        if not isinstance(args, dict):
            bad_arguments += 1
            valid += 1
            continue
        errors = validate(args, props, required)
        if errors:
            invalid += 1
        else:
            valid += 1
        for error in errors:
            rows.append((call_id, error))
        total_errors += len(errors)

    lines = ["call_id,error"] + [f"{call_id},{error}" for call_id, error in rows]
    (out_dir / "errors.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "calls": calls,
        "valid": valid,
        "invalid": invalid,
        "errors": total_errors,
        "wrong_tool": wrong_tool,
        "bad_arguments": bad_arguments,
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, separators=(",", ":")) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
