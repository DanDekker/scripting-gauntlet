#!/usr/bin/env python3
"""025-groupby-aggregate — composite key, one accumulator, sort at the end."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

groups: dict[tuple[str, str], list[float]] = {}
rows_in = skipped = 0

with (inp / "sales.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    next(reader, None)
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        rows_in += 1
        date, region, _rep, amount = (row + [""] * 4)[:4]
        amount = amount.strip()
        if not amount:
            skipped += 1
            continue
        bucket = groups.setdefault((region.strip().lower(), date.strip()[:7]), [0, 0.0])
        bucket[0] += 1
        bucket[1] += float(amount)

with (out / "rollup.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["region", "month", "orders", "revenue", "avg_order"])
    for (region, month), (orders, revenue) in sorted(groups.items()):
        writer.writerow([region, month, orders, f"{revenue:.2f}", f"{revenue / orders:.2f}"])

summary = {
    "rows_in": rows_in,
    "skipped": skipped,
    "groups": len(groups),
    "revenue": round(sum(bucket[1] for bucket in groups.values()), 2),
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
