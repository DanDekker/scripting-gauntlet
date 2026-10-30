#!/usr/bin/env python3
"""247-ps1-format-object — portable reference."""

import csv
import json
import os
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
rows = []
healthy = down = slow = 0
with (inp / "services.csv").open(newline="", encoding="utf-8") as fh:
    for source in csv.DictReader(fh):
        latency = int(source["latency_ms"])
        is_healthy = source["status"] == "up" and latency <= 100
        healthy += is_healthy
        down += source["status"] == "down"
        slow += latency > 100
        rows.append((source["name"], source["status"], latency, source["owner"], "yes" if is_healthy else "no"))

out.mkdir(parents=True, exist_ok=True)
with (out / "report.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["name", "status", "latency_ms", "owner", "healthy"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps(
        {"services": len(rows), "healthy": healthy, "down": down, "slow": slow},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
