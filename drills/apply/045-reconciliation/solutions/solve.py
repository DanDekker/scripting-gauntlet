#!/usr/bin/env python3
"""045-reconciliation — uppercase the key, sum per side, classify by presence then delta."""

import csv
import json
import os
from pathlib import Path



def money(cell: str) -> float:
    text = cell.strip()
    sign = 1.0
    if text.startswith("(") and text.endswith(")"):
        sign, text = -1.0, text[1:-1]
    return sign * float(text.replace("$", "").replace(" ", "") or 0)


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

ledger: dict[str, float] = {}
bank: dict[str, float] = {}
for name, target, column in (("ledger.csv", ledger, 2), ("bank.csv", bank, 1)):
    with (inp / name).open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        next(reader, None)
        for row in reader:
            if not any(cell.strip() for cell in row):
                continue
            ref = row[0].strip().upper()
            target[ref] = target.get(ref, 0.0) + money(row[column])

rows = []
for ref in sorted(set(ledger) | set(bank)):
    has_ledger, has_bank = ref in ledger, ref in bank
    left, right = ledger.get(ref, 0.0), bank.get(ref, 0.0)
    delta = left - right
    if not has_ledger:
        status = "missing_in_ledger"
    elif not has_bank:
        status = "missing_in_bank"
    elif abs(delta) > 0.005:
        status = "amount_mismatch"
    else:
        status = "matched"
    rows.append((ref, left, right, delta, status))

with (out / "recon.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("ref,ledger_total,bank_total,delta,status\n")
    for ref, left, right, delta, status in rows:
        fh.write(f"{ref},{left:.2f},{right:.2f},{delta:.2f},{status}\n")

counts = {key: sum(1 for row in rows if row[4] == key) for key in (
    "matched", "amount_mismatch", "missing_in_bank", "missing_in_ledger")}
ledger_total = round(sum(ledger.values()), 2)
bank_total = round(sum(bank.values()), 2)
(out / "summary.json").write_text(
    json.dumps(
        {
            "refs": len(rows),
            **counts,
            "ledger_total": ledger_total,
            "bank_total": bank_total,
            "delta": round(ledger_total - bank_total, 2),
        }
    )
    + "\n",
    encoding="utf-8",
)
