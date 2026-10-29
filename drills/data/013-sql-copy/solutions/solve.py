#!/usr/bin/env python3
"""013-sql-copy — walk the dump, keep only the block we asked for."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

rows = []
inside = False
for line in (inp / "dump.sql").read_text(encoding="utf-8").splitlines():
    if line.startswith("COPY public.orders "):
        inside = True
        continue
    if line.strip() == "\\.":
        inside = False
        continue
    if not inside or not line.strip():
        continue
    parts = line.split("\t")
    rows.append((parts[0], parts[1], parts[2], float(parts[3])))

with (out / "orders.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["id", "customer", "region", "amount"])
    writer.writerows(rows)

summary = {"rows": len(rows), "total": round(sum(row[3] for row in rows), 2)}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
