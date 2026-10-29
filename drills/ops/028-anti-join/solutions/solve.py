#!/usr/bin/env python3
"""028-anti-join — a set of active ids, then a membership test per customer."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

CUTOFF = "2026-02-01"

customers: list[tuple[str, str]] = []
known: set[str] = set()
with (inp / "customers.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    next(reader, None)
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        key, name = (cell.strip() for cell in (row + [""] * 2)[:2])
        key = key.lower()
        if key in known:
            continue
        known.add(key)
        customers.append((key, name))

active: set[str] = set()
with (inp / "orders.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    next(reader, None)
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        _oid, key, order_date, _amount = (cell.strip() for cell in (row + [""] * 4)[:4])
        key = key.lower()
        if order_date >= CUTOFF and key in known:
            active.add(key)

inactive = sorted((key, name) for key, name in customers if key not in active)

with (out / "inactive.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["customer_id", "name"])
    writer.writerows(inactive)

summary = {
    "customers": len(customers),
    "active": len(customers) - len(inactive),
    "inactive": len(inactive),
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
