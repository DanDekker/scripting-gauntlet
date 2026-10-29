#!/usr/bin/env python3
"""006-ragged-rows — pad short rows, drop surplus fields, count both."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

with (inp / "orders.csv").open(newline="", encoding="utf-8") as fh:
    rows = list(csv.reader(fh))

header = rows[0]
width = len(header)
clean = [header]
padded = truncated = 0

for row in rows[1:]:
    if len(row) < width:
        row = row + [""] * (width - len(row))
        padded += 1
    elif len(row) > width:
        row = row[:width]
        truncated += 1
    clean.append(row)

with (out / "clean.csv").open("w", newline="", encoding="utf-8") as fh:
    csv.writer(fh, lineterminator="\n").writerows(clean)

summary = {"rows": len(clean) - 1, "padded": padded, "truncated": truncated}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
