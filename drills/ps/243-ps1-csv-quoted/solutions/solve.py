#!/usr/bin/env python3
"""243-ps1-csv-quoted — portable reference."""

import csv
import json
import os
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
rows = []
grand_total = Decimal("0")
zero_quantity = 0

with (inp / "invoices.csv").open(newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        units = int(row["units"])
        unit_price = Decimal(row["unit_price"])
        total = (units * unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        rows.append((row["order_id"], row["customer"], units, f"{unit_price:.2f}", f"{total:.2f}"))
        grand_total += total
        zero_quantity += units == 0

out.mkdir(parents=True, exist_ok=True)
with (out / "invoices.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["order_id", "customer", "units", "unit_price", "total"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps(
        {"orders": len(rows), "grand_total": float(grand_total), "zero_quantity": zero_quantity},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
