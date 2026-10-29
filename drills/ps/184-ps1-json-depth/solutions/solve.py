#!/usr/bin/env python3
"""184-ps1-json-depth — same contract; python's json has no depth limit, so the echo is
the easy half and the flatten is the work."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

config = json.loads((IN / "config.json").read_text(encoding="utf-8"))

rows = []


def walk(value, prefix):
    if value is None:
        rows.append((prefix, "null", ""))
    elif isinstance(value, bool):
        rows.append((prefix, "bool", "true" if value else "false"))
    elif isinstance(value, (int, float)):
        rows.append((prefix, "int", str(value)))
    elif isinstance(value, list):
        rows.append((prefix, "array", "|".join(str(item) for item in value)))
    elif isinstance(value, dict):
        for key, child in value.items():
            walk(child, f"{prefix}.{key}" if prefix else key)
    else:
        rows.append((prefix, "string", str(value)))


walk(config, "")
rows.sort(key=lambda row: row[0].encode())

with (OUT / "flat.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("key,type,value\n")
    for row in rows:
        fh.write(",".join(row) + "\n")

(OUT / "echo.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
(OUT / "summary.json").write_text(
    json.dumps(
        {
            "keys": len(rows),
            "nulls": sum(1 for _k, kind, _v in rows if kind == "null"),
            "arrays": sum(1 for _k, kind, _v in rows if kind == "array"),
        }
    )
    + "\n",
    encoding="utf-8",
)
