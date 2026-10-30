#!/usr/bin/env python3
"""208-perl-crlf-strip — python twin."""

import json
import os
import re
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

raw = (IN / "measurements.csv").read_bytes().decode("utf-8")
lines = raw.split("\r\n")
if lines and lines[-1] == "":
    lines.pop()

rows = []
for line in lines[1:]:
    if line == "":
        continue
    sensor, label, value = line.split(",")
    status = "ok" if re.match(r"^[0-9]+\.[0-9]+$", value) else "malformed"
    rows.append((sensor, label, value, status))

valid = sum(1 for row in rows if row[3] == "ok")
malformed = len(rows) - valid

with (OUT / "readings.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("sensor,label,value,status\n")
    for row in rows:
        fh.write(f"{row[0]},{row[1]},{row[2]},{row[3]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {"readings": len(rows), "valid": valid, "malformed": malformed},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
