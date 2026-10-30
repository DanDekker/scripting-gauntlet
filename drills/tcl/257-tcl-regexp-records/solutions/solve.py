#!/usr/bin/env python3
"""257-tcl-regexp-records — portable reference."""

import csv
import json
import os
import re
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
pattern = re.compile(r"^\[(INFO|WARN|ERROR)\] worker=([-A-Za-z0-9_.]+) duration=([0-9]+)ms$")
rows = []
skipped = slow = 0
for raw in (inp / "events.log").read_text(encoding="utf-8").splitlines():
    if not raw.strip():
        continue
    match = pattern.fullmatch(raw)
    if not match:
        skipped += 1
        continue
    level, worker, duration_text = match.groups()
    duration = int(duration_text)
    is_slow = duration > 100
    slow += is_slow
    rows.append((level, worker, duration, "yes" if is_slow else "no"))

out.mkdir(parents=True, exist_ok=True)
with (out / "events.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["level", "worker", "duration", "slow"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps({"records": len(rows), "skipped": skipped, "slow": slow}, separators=(",", ":"))
    + "\n",
    encoding="utf-8",
)
