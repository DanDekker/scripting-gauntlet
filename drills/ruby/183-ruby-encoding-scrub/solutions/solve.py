#!/usr/bin/env python3
"""183-ruby-encoding-scrub — same contract; decode strictly, then decode leniently with
U+FFFD mapped to the same '?' replacement."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

lines = (IN / "raw.txt").read_bytes().split(b"\n")
if lines and lines[-1] == b"":
    lines.pop()  # a trailing newline is not an extra record
invalid = 0
rows = []

for index, raw in enumerate(lines, start=1):
    try:
        text = raw.decode("utf-8")
        valid = True
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="replace").replace("\ufffd", "?")
        valid = False
        invalid += 1
    rows.append((index, "true" if valid else "false", len(text), len(raw), text))

with (OUT / "lines.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("line,valid,chars,bytes,text\n")
    for row in rows:
        fh.write(",".join(str(cell) for cell in row) + "\n")

(OUT / "summary.json").write_text(
    json.dumps({"lines": len(rows), "invalid": invalid}) + "\n", encoding="utf-8"
)
