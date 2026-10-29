#!/usr/bin/env python3
"""156-lua-sparse-array — same contract; positions are tracked explicitly."""

import json
import os
import re
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

INTEGER_RE = re.compile(r"^-?\d+$")

values: dict[int, int] = {}
positions = present = invalid = 0

for raw in (IN / "values.txt").read_text(encoding="utf-8").splitlines():
    positions += 1
    line = raw.strip()
    if not line:
        continue
    if not INTEGER_RE.match(line):
        invalid += 1
        continue
    values[positions] = int(line)
    present += 1

with (OUT / "present.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("position,value\n")
    for position in range(1, positions + 1):
        if position in values:
            fh.write(f"{position},{values[position]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "positions": positions,
            "present": present,
            "missing": positions - present,
            "invalid": invalid,
            "total": sum(values.values()),
            "max": max(values.values(), default=0),
        }
    )
    + "\n",
    encoding="utf-8",
)
