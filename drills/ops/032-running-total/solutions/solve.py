#!/usr/bin/env python3
"""032-running-total — sort first, then accumulate per account."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

rows = []
with (inp / "ledger.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    next(reader, None)
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        tx_id, date, account, amount = (cell.strip() for cell in (row + [""] * 4)[:4])
        rows.append((account.lower(), date, int(tx_id), float(amount)))

rows.sort(key=lambda r: (r[0], r[1], r[2]))

out_rows = []
account = None
balance = 0.0
for acct, date, _tx_id, amount in rows:
    if acct != account:
        account, balance = acct, 0.0
    balance += amount
    out_rows.append((acct, date, amount, balance))

with (out / "running.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["account", "date", "amount", "balance"])
    for acct, date, amount, bal in out_rows:
        writer.writerow([acct, date, f"{amount:.2f}", f"{bal:.2f}"])

summary = {
    "accounts": len({row[0] for row in rows}),
    "transactions": len(rows),
    "net": round(sum(row[3] for row in rows), 2),
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
