#!/usr/bin/env python3
"""242-ps1-tryparse — portable reference."""

import csv
import json
import os
import re
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
rows = []
rejected = 0
total = 0

with (inp / "measurements.csv").open(newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        text = row["raw"].strip()
        if not re.fullmatch(r"[+-]?\d+", text):
            rejected += 1
            continue
        value = int(text)
        if not -(2**31) <= value <= 2**31 - 1:
            rejected += 1
            continue
        rows.append((row["name"], value))
        total += value

out.mkdir(parents=True, exist_ok=True)
with (out / "readings.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("name,value\n")
    for name, value in rows:
        fh.write(f"{name},{value}\n")
(out / "summary.json").write_text(
    json.dumps({"accepted": len(rows), "rejected": rejected, "total": total}, separators=(",", ":"))
    + "\n",
    encoding="utf-8",
)
