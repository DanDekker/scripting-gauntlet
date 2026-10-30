#!/usr/bin/env python3
"""213-perl-truthy-zero — python twin implementing perl's truth rule."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

rows = []
for index, line in enumerate((IN / "settings.txt").read_text(encoding="utf-8").splitlines(), start=1):
    if line == "":
        continue
    name, _, value = line.partition(" ")
    # Perl truth: only the empty string and the exact text "0" are false.
    state = "off" if value in ("", "0") else "on"
    rows.append((index, name, value, state))

on = sum(1 for row in rows if row[3] == "on")

with (OUT / "settings.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("index,name,value,state\n")
    for row in rows:
        fh.write(f"{row[0]},{row[1]},{row[2]},{row[3]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {"settings": len(rows), "on": on, "off": len(rows) - on},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
