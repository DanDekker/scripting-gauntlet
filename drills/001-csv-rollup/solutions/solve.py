#!/usr/bin/env python3
"""001-csv-rollup — dedupe by order_id (latest wins), keep paid, roll up by region."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

# order_id -> the latest version of that order
latest = {}
with (inp / "orders.csv").open(newline="", encoding="utf-8-sig") as fh:
    for row in csv.DictReader(fh):
        order_id = (row.get("order_id") or "").strip()
        if not order_id:
            continue
        stamp = (row.get("updated_at") or "").strip()
        if order_id not in latest or stamp > latest[order_id]["updated_at"]:
            latest[order_id] = {
                "region": (row.get("region") or "").strip(),
                "status": (row.get("status") or "").strip().lower(),
                "amount": (row.get("amount") or "").strip(),
                "updated_at": stamp,
            }

regions: dict[str, list] = {}
orders = dropped = 0
revenue = 0.0

for row in latest.values():
    if row["status"] != "paid":
        continue
    raw = row["amount"].replace("$", "").replace(",", "").strip()
    try:
        amount = float(raw)
    except ValueError:
        dropped += 1
        continue

    name = row["region"][:1].upper() + row["region"][1:].lower()
    bucket = regions.setdefault(name, [0, 0.0])
    bucket[0] += 1
    bucket[1] += amount
    orders += 1
    revenue += amount

with (out / "regions.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("region,orders,revenue\n")
    for name, (count, total) in sorted(regions.items(), key=lambda kv: (-kv[1][1], kv[0])):
        fh.write(f"{name},{count},{total:.2f}\n")

summary = {
    "orders": orders,
    "regions": len(regions),
    "revenue": round(revenue, 2),
    "dropped": dropped,
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
