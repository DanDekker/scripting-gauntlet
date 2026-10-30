#!/usr/bin/env python3
"""240-ps1-split-regex — python twin; str.split is literal, which is the point."""

import json
import os
import re
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

rows = []
malformed = 0
total = 0
packages = set()

for raw in (IN / "builds.log").read_text(encoding="utf-8").splitlines():
    text = raw.strip()
    if not text or text.startswith("#"):
        continue

    fields = text.split("|")  # literal, unlike PowerShell's regex -split
    if len(fields) != 4:
        malformed += 1
        continue

    pkg, ver, sha, size_text = (cell.strip() for cell in fields)
    if not pkg or not re.fullmatch(r"\d+\.\d+\.\d+", ver) or not re.fullmatch(r"\d+", size_text):
        malformed += 1
        continue

    major, minor, patch = (int(part) for part in ver.split("."))
    size = int(size_text)
    total += size
    packages.add(pkg)
    rows.append((pkg, major, minor, patch, sha, size))

if rows:
    with (OUT / "builds.csv").open("w", encoding="utf-8", newline="") as fh:
        fh.write("pkg,major,minor,patch,sha,size\n")
        for row in rows:
            fh.write(",".join(str(cell) for cell in row) + "\n")
else:
    (OUT / "builds.csv").write_text("pkg,major,minor,patch,sha,size\n", encoding="utf-8")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "rows": len(rows),
            "malformed": malformed,
            "total_size": total,
            "packages": len(packages),
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
