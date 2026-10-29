#!/usr/bin/env python3
"""012-markdown-table — find the pipe rows, drop the separator, trim the cells."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

rows = []
for line in (inp / "report.md").read_text(encoding="utf-8").splitlines():
    if not line.startswith("|"):
        continue
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if all(set(cell) <= set("-: ") for cell in cells):  # separator row
        continue
    if cells[0].lower() == "region":  # header
        continue
    rows.append((cells[0], int(cells[1]), float(cells[2])))

with (out / "table.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["region", "qty", "revenue"])
    writer.writerows(rows)

summary = {
    "rows": len(rows),
    "total_qty": sum(row[1] for row in rows),
    "total_revenue": round(sum(row[2] for row in rows), 2),
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
