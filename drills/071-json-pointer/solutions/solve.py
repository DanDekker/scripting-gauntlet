#!/usr/bin/env python3
"""071-json-pointer - split, then unescape, then walk."""

import json
import os
import re
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

INDEX = re.compile(r"0|[1-9][0-9]*")
MISS = object()


def resolve(doc, pointer: str):
    if not pointer.startswith("/"):
        raise SystemExit(f"pointer must start with /: {pointer}")
    tokens = [t.replace("~1", "/").replace("~0", "~") for t in pointer.split("/")[1:]]
    current = doc
    for token in tokens:
        if isinstance(current, dict):
            if token not in current:
                return MISS
            current = current[token]
        elif isinstance(current, list):
            if not INDEX.fullmatch(token):
                return MISS
            position = int(token)
            if position >= len(current):
                return MISS
            current = current[position]
        else:
            return MISS
    return current


def render(value) -> str:
    if value is MISS or value is None or isinstance(value, (dict, list)):
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


doc = json.loads((inp / "doc.json").read_text(encoding="utf-8"))
rows = []
found = 0
for raw in (inp / "paths.txt").read_text(encoding="utf-8").splitlines():
    pointer = raw.strip()
    if not pointer or pointer.startswith("#"):
        continue
    value = render(resolve(doc, pointer))
    if value != "":
        found += 1
    rows.append((pointer, value))

with (out / "values.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("path,value\n")
    for pointer, value in rows:
        fh.write(f"{pointer},{value}\n")

summary = {"paths": len(rows), "found": found, "missing": len(rows) - found}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
