#!/usr/bin/env python3
"""027-join-lookup — dict of customers, then a left join over the orders."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

lookup: dict[str, tuple[str, str]] = {}
with (inp / "customers.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    next(reader, None)
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        cid, name, country = (cell.strip() for cell in (row + [""] * 3)[:3])
        lookup[cid.lower()] = (name, country)

rows = []
matched = unmatched = 0
total = 0.0
with (inp / "orders.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    next(reader, None)
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        oid, cid, amount = (cell.strip() for cell in (row + [""] * 3)[:3])
        key = cid.lower()
        hit = lookup.get(key)
        if hit is None:
            name, country = "UNKNOWN", "??"
            unmatched += 1
        else:
            name, country = hit
            matched += 1
        value = float(amount)
        total += value
        rows.append((oid, key, name, country, value))

rows.sort(key=lambda r: r[0])

with (out / "enriched.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["order_id", "customer_id", "name", "country", "amount"])
    for oid, key, name, country, value in rows:
        writer.writerow([oid, key, name, country, f"{value:.2f}"])

summary = {
    "orders": len(rows),
    "matched": matched,
    "unmatched": unmatched,
    "total": round(total, 2),
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
