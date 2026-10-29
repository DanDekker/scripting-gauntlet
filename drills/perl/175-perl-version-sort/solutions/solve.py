#!/usr/bin/env python3
"""175-perl-version-sort — same contract; a tuple of integers is the semantic key."""

import json
import os
import re
from pathlib import Path

VERSION = re.compile(r"^[0-9]+(\.[0-9]+)*$")

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

rows = []
lines = invalid = 0

for raw in (IN / "releases.txt").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    lines += 1
    parts = line.split()
    if len(parts) < 2 or not VERSION.match(parts[1]):
        invalid += 1
        continue
    name, version = parts[0], parts[1]
    rows.append((name, version, tuple(int(part) for part in version.split("."))))

rows.sort(key=lambda row: (tuple(-part for part in row[2]), row[0]))

with (OUT / "ordered.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("rank,name,version\n")
    for rank, (name, version, _key) in enumerate(rows, start=1):
        fh.write(f"{rank},{name},{version}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "lines": lines,
            "ordered": len(rows),
            "invalid": invalid,
            "newest": rows[0][0] if rows else "",
        }
    )
    + "\n",
    encoding="utf-8",
)
