#!/usr/bin/env python3
"""219-perl-undef-vs-empty — python twin (a missing key is absent, not empty)."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

cfg = {}
for line in (IN / "config.ini").read_text(encoding="utf-8").splitlines():
    if not line:
        continue
    key, _, value = line.partition("=")
    cfg[key] = value

wanted = [
    line
    for line in (IN / "wanted.txt").read_text(encoding="utf-8").splitlines()
    if line
]

rows = []
counts = {"set": 0, "empty": 0, "missing": 0}
for index, key in enumerate(wanted, start=1):
    if key not in cfg:
        status, value = "missing", ""
    elif cfg[key] == "":
        status, value = "empty", ""
    else:
        status, value = "set", cfg[key]
    counts[status] += 1
    rows.append((index, key, status, value))

with (OUT / "settings.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("index,key,status,value\n")
    for row in rows:
        fh.write(f"{row[0]},{row[1]},{row[2]},{row[3]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "wanted": len(rows),
            "set": counts["set"],
            "empty": counts["empty"],
            "missing": counts["missing"],
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
