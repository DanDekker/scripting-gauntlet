#!/usr/bin/env python3
"""245-ps1-utf16 — portable reference."""

import csv
import json
import os
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
rows = []
counts = {"INFO": 0, "WARN": 0, "ERROR": 0}
for raw in (inp / "events.log").read_text(encoding="utf-16-le").splitlines():
    text = raw.strip()
    if not text:
        continue
    level, message = (part.strip() for part in text.split("|", 1))
    if level not in counts:
        raise ValueError(f"unknown level: {level}")
    counts[level] += 1
    rows.append((level, message))

out.mkdir(parents=True, exist_ok=True)
with (out / "events.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["level", "message"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps(
        {"records": len(rows), "info": counts["INFO"], "warn": counts["WARN"], "error": counts["ERROR"]},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
