#!/usr/bin/env python3
"""030-pivot-melt — read the header, then emit one row per non-empty cell."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

rows = []
total = 0.0
regions: set[str] = set()

with (inp / "wide.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    header = [cell.strip().lower() for cell in next(reader)]
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        region = row[0].strip().lower()
        regions.add(region)
        for quarter, cell in zip(header[1:], row[1:]):
            value = cell.strip()
            if not value:
                continue
            amount = float(value)
            total += amount
            rows.append((region, quarter, amount))

rows.sort(key=lambda r: (r[0], r[1]))

with (out / "long.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["region", "quarter", "amount"])
    for region, quarter, amount in rows:
        writer.writerow([region, quarter, f"{amount:.2f}"])

summary = {"regions": len(regions), "cells": len(rows), "total": round(total, 2)}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
