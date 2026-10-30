#!/usr/bin/env python3
"""214-perl-split-captures — python twin."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

rows = []
for line in (IN / "access.log").read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    fields = line.split()
    if len(fields) < 4:
        continue
    rows.append(fields[:4])

ok = 0
errors = 0

with (OUT / "access.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("index,timestamp,method,path,status\n")
    for index, row in enumerate(rows, start=1):
        fh.write(f"{index},{','.join(row)}\n")
        if row[3].startswith("2"):
            ok += 1
        else:
            errors += 1

(OUT / "summary.json").write_text(
    json.dumps(
        {"records": len(rows), "ok": ok, "errors": errors},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
