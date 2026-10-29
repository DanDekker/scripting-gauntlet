#!/usr/bin/env python3
"""177-ps1-decimal-money — same contract; Decimal with ROUND_HALF_UP is the exact route."""

import csv
import json
import os
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

CENT = Decimal("0.01")

sums: dict[str, Decimal] = {}
counts: dict[str, int] = {}

with (IN / "amounts.csv").open(newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        account = row["account"]
        sums[account] = sums.get(account, Decimal(0)) + Decimal(row["amount"].strip())
        counts[account] = counts.get(account, 0) + 1

records = []
for account in sorted(sums, key=lambda name: name.encode()):
    exact = sums[account]
    rounded = exact.quantize(CENT, rounding=ROUND_HALF_UP)
    third = abs((exact * 1000) % 10)
    records.append((account, format(rounded, "f"), counts[account], third == 5))

with (OUT / "totals.csv").open("w", encoding="utf-8", newline="") as fh:
    writer = csv.writer(fh)
    writer.writerow(["account", "total", "items"])
    for account, total, items, _half in records:
        writer.writerow([account, total, items])

grand = sum(
    (Decimal(total) for _account, total, _items, _half in records), Decimal(0)
).quantize(CENT, rounding=ROUND_HALF_UP)

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "accounts": len(records),
            "total": format(grand, "f"),
            "half_cents": sum(1 for *_rest, half in records if half),
        }
    )
    + "\n",
    encoding="utf-8",
)
