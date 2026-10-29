#!/usr/bin/env python3
"""008-fixed-width — slice the record, do not split it."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

records = 0
blank_names = 0
rows = [["name", "dept", "qty", "price", "total"]]

for line in (inp / "inventory.dat").read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    name = line[0:8].strip()
    dept = line[8:14].strip()
    qty = int(line[14:18].strip())
    price = float(line[18:27].strip())
    if name == "":
        blank_names += 1
    rows.append([name, dept, str(qty), f"{price:.2f}", f"{qty * price:.2f}"])
    records += 1

with (out / "inventory.csv").open("w", newline="", encoding="utf-8") as fh:
    csv_writer = fh
    for row in rows:
        csv_writer.write(",".join(row) + "\n")

summary = {"records": records, "blank_names": blank_names}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
