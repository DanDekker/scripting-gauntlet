#!/usr/bin/env python3
"""026-topn-per-group — one sort, then a counter per group."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

rows = []
with (inp / "sales.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    next(reader, None)
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        region, rep, amount = (row + [""] * 3)[:3]
        rows.append((region.strip().lower(), rep.strip(), float(amount.strip())))

rows.sort(key=lambda r: (r[0], -r[2], r[1]))

out_rows = []
current = None
rank = 0
for region, rep, revenue in rows:
    if region != current:
        current, rank = region, 0
    rank += 1
    if rank <= 2:
        out_rows.append((region, rank, rep, revenue))

with (out / "top2.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["region", "rank", "rep", "revenue"])
    for region, rank, rep, revenue in out_rows:
        writer.writerow([region, rank, rep, f"{revenue:.2f}"])

summary = {
    "regions": len({row[0] for row in rows}),
    "rows_in": len(rows),
    "rows_out": len(out_rows),
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
