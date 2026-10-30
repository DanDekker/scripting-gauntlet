#!/usr/bin/env python3
"""223-perl-list-repetition — python twin."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

count = 0
template = ""
for line in (IN / "spec.txt").read_text(encoding="utf-8").splitlines():
    if not line:
        continue
    key, _, value = line.partition("=")
    if key == "count":
        count = int(value)
    elif key == "template":
        template = value

rows = [template] * count

(OUT / "report.txt").write_text(
    "".join(row + "\n" for row in rows), encoding="utf-8"
)

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "count": count,
            "lines": len(rows),
            "chars": sum(len(row) for row in rows),
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
