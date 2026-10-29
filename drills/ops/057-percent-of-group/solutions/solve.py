#!/usr/bin/env python3
"""057-percent-of-group — totals first, then one ordered walk per group."""

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
        region, rep, amount = (cell.strip() for cell in (row + [""] * 3)[:3])
        rows.append((region.lower(), rep, float(amount)))

rows.sort(key=lambda r: (r[0], -r[2], r[1]))
totals: dict[str, float] = {}
for region, _rep, amount in rows:
    totals[region] = totals.get(region, 0.0) + amount

shares = []
running: dict[str, float] = {}
for region, rep, amount in rows:
    running[region] = running.get(region, 0.0) + amount
    total = totals[region]
    shares.append(
        (
            region,
            rep,
            f"{amount:.2f}",
            f"{100 * amount / total:.2f}",
            f"{100 * running[region] / total:.2f}",
        )
    )

with (out / "shares.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["region", "rep", "amount", "pct", "cum_pct"])
    writer.writerows(shares)

summary = {"rows": len(rows), "groups": len(totals), "total": round(sum(totals.values()), 2)}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
