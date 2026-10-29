#!/usr/bin/env python3
"""023-filter-predicate — trim, lowercase, one predicate, then sort."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

SHIPS_TO = {"west", "east", "north"}
kept = []
rows_in = 0
total = 0.0

with (inp / "orders.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    next(reader, None)
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        rows_in += 1
        oid, cust, region, status, amount = (row + [""] * 5)[:5]
        oid, cust = oid.strip(), cust.strip()
        region, status = region.strip().lower(), status.strip().lower()
        value = float(amount.strip().removeprefix("$"))
        if status != "paid" or value < 100 or region not in SHIPS_TO:
            continue
        total += value
        kept.append((oid, cust, region, status, value))

kept.sort(key=lambda r: (-r[4], r[0]))

with (out / "kept.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["order_id", "customer", "region", "status", "amount"])
    for oid, cust, region, status, value in kept:
        writer.writerow([oid, cust, region, status, f"{value:.2f}"])

summary = {
    "rows_in": rows_in,
    "kept": len(kept),
    "dropped": rows_in - len(kept),
    "total": round(total, 2),
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
