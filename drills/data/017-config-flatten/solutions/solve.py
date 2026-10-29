#!/usr/bin/env python3
"""017-config-flatten — a small indentation walker, no yaml dependency."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)


def scalar(value: str):
    try:
        return int(value)
    except ValueError:
        return value


flat: dict[str, object] = {}
stack: list[tuple[int, str]] = []
lists: dict[str, int] = {}

for raw in (inp / "app.yaml").read_text(encoding="utf-8").splitlines():
    if not raw.strip() or raw.lstrip().startswith("#"):
        continue
    indent = len(raw) - len(raw.lstrip(" "))
    body = raw.strip()

    while stack and stack[-1][0] >= indent:
        stack.pop()
    parent = ".".join(key for _, key in stack)

    if body.startswith("- "):
        index = lists.get(parent, 0)
        lists[parent] = index + 1
        flat[f"{parent}.{index}"] = body[2:].strip()
        continue

    key, _, value = body.partition(":")
    key = key.strip()
    value = value.strip()
    if value == "":
        stack.append((indent, key))
    else:
        flat[f"{parent}.{key}" if parent else key] = scalar(value)

(out / "flat.json").write_text(
    json.dumps(flat, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
(out / "summary.json").write_text(json.dumps({"keys": len(flat)}) + "\n", encoding="utf-8")
