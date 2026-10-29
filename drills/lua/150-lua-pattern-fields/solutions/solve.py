#!/usr/bin/env python3
"""150-lua-pattern-fields — same contract, standard library only."""

import json
import os
import re
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

KEY_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def csv_field(value: str) -> str:
    if "," in value or '"' in value or "\n" in value or "\r" in value:
        return '"' + value.replace('"', '""') + '"'
    return value


values: dict[str, str] = {}
order: list[str] = []
duplicates = 0
invalid = 0

for raw in (IN / "report.txt").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    if "=" not in line:
        invalid += 1
        continue
    key, _, value = line.partition("=")
    key = key.strip()
    if not key or not KEY_RE.match(key):
        invalid += 1
        continue
    value = value.strip()
    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    if key in values:
        duplicates += 1
    else:
        order.append(key)
    values[key] = value

order.sort(key=lambda k: k.encode())

with (OUT / "fields.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("key,value\n")
    for key in order:
        fh.write(f"{csv_field(key)},{csv_field(values[key])}\n")

(OUT / "summary.json").write_text(
    json.dumps({"keys": len(order), "duplicates": duplicates, "invalid": invalid}) + "\n",
    encoding="utf-8",
)
