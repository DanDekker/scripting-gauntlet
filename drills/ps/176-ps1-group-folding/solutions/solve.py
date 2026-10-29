#!/usr/bin/env python3
"""176-ps1-group-folding — same contract; python's dict keying is already case-sensitive,
so the work is the ordinal sort and counting the empty amounts."""

import csv
import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

buckets: dict[str, dict] = {}
rows_total = 0

with (IN / "items.csv").open(newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        rows_total += 1
        key = row["group"] or ""
        bucket = buckets.setdefault(key, {"count": 0, "total": 0, "missing": 0})
        bucket["count"] += 1
        amount = (row.get("amount") or "").strip()
        if not amount:
            bucket["missing"] += 1
            continue
        try:
            bucket["total"] += int(amount)
        except ValueError:
            raise SystemExit(f"items.csv: id {row.get('id')}: amount is not a number: '{amount}'")

ordered = sorted(buckets, key=lambda name: name.encode())
with (OUT / "groups.csv").open("w", encoding="utf-8", newline="") as fh:
    writer = csv.writer(fh)
    writer.writerow(["group", "count", "total", "missing"])
    for name in ordered:
        bucket = buckets[name]
        writer.writerow([name, bucket["count"], bucket["total"], bucket["missing"]])

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "groups": len(ordered),
            "items": rows_total,
            "missing": sum(b["missing"] for b in buckets.values()),
        }
    )
    + "\n",
    encoding="utf-8",
)
