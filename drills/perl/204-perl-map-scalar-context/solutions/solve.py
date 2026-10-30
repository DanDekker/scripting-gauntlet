#!/usr/bin/env python3
"""204-perl-map-scalar-context — python twin."""

import csv
import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

rows = []
with (IN / "invoices.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    next(reader, None)
    for record in reader:
        if not record:
            continue
        invoice_id, customer, amount, status = (record + ["", "", "", ""])[:4]
        rows.append({"id": invoice_id, "customer": customer, "amount": amount, "status": status})

paid = [row for row in rows if row["status"] == "paid"]
paid_count = len(paid)
paid_total = sum(float(row["amount"]) for row in paid)

largest_paid_id = ""
largest_amount = None
for row in paid:
    amount = float(row["amount"])
    if largest_amount is None or amount > largest_amount:
        largest_amount = amount
        largest_paid_id = row["id"]

with (OUT / "paid.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("id,amount\n")
    for row in paid:
        fh.write(f"{row['id']},{row['amount']}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "invoices": len(rows),
            "paid_count": paid_count,
            "paid_total": round(paid_total, 2),
            "unpaid_count": len(rows) - paid_count,
            "largest_paid_id": largest_paid_id,
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
