#!/usr/bin/env python3
"""203-perl-slurp-record-separator — python twin."""

import json
import os
import re
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

config = (IN / "config.ini").read_text(encoding="utf-8")

config_lines = config.count("\n")

settings = 0
for line in config.split("\n"):
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        continue
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", stripped):
        settings += 1

# Paragraph mode: records are separated by a blank line.
text = (IN / "notes.txt").read_text(encoding="utf-8")
records = []
for block in re.split(r"\n[ \t]*\n", text):
    block = block.strip("\n")
    if block == "":
        continue
    records.append(block)

rows = []
total_lines = 0
for index, record in enumerate(records, start=1):
    lines = record.split("\n")
    rows.append((index, lines[0], len(lines)))
    total_lines += len(lines)

with (OUT / "records.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("index,title,lines\n")
    for index, title, count in rows:
        fh.write(f"{index},{title},{count}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "records": len(rows),
            "total_lines": total_lines,
            "config_lines": config_lines,
            "settings": settings,
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
