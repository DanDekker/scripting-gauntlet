#!/usr/bin/env python3
"""253-jxa-objc-errors — portable reference."""

import csv
import json
import os
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
rows = []
ok = missing = total_bytes = 0
with (inp / "jobs.csv").open(newline="", encoding="utf-8") as fh:
    for source in csv.DictReader(fh):
        path = inp / source["path"].strip()
        if not path.is_file():
            missing += 1
            rows.append((source["id"].strip(), "missing", 0, "not found"))
            continue
        size = path.stat().st_size
        ok += 1
        total_bytes += size
        rows.append((source["id"].strip(), "ok", size, ""))

out.mkdir(parents=True, exist_ok=True)
with (out / "checks.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["id", "status", "bytes", "message"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps({"jobs": len(rows), "ok": ok, "missing": missing, "bytes": total_bytes}, separators=(",", ":"))
    + "\n",
    encoding="utf-8",
)
