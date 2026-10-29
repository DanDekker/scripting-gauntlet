#!/usr/bin/env python3
"""046-quality-profile — bucket per column, then report."""

import csv
import json
import os
import re
from collections import Counter
from pathlib import Path

NUMERIC = re.compile(r"-?[0-9]+(\.[0-9]+)?$")
NULLS = {"null", "n/a", "na", "none", "-"}

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

columns: list[str] = []
values: dict[str, list[str]] = {}
nulls: Counter = Counter()
rows = 0

with (inp / "customers.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    columns = [cell.strip() for cell in next(reader)]
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        rows += 1
        for index, name in enumerate(columns):
            cell = row[index].strip() if index < len(row) else ""
            if not cell or cell.lower() in NULLS:
                nulls[name] += 1
                continue
            values.setdefault(name, []).append(cell)

profile, total_nulls = [], 0
for name in sorted(columns):
    vals = values.get(name, [])
    counts = Counter(vals)
    first: dict[str, int] = {}
    for position, value in enumerate(vals):
        first.setdefault(value, position)
    top_value, top_count = "", 0
    if counts:
        top_value = min(counts, key=lambda v: (-counts[v], first[v]))
        top_count = counts[top_value]
    numeric = "yes" if vals and all(NUMERIC.match(v) for v in vals) else "no"
    low = f"{min(float(v) for v in vals):.2f}" if numeric == "yes" else ""
    high = f"{max(float(v) for v in vals):.2f}" if numeric == "yes" else ""
    total_nulls += nulls[name]
    profile.append((name, len(vals), nulls[name], len(counts), numeric, low, high, top_value, top_count))

with (out / "profile.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("column,non_null,nulls,distinct,numeric,min,max,top_value,top_count\n")
    for row in profile:
        fh.write(",".join(str(cell) for cell in row) + "\n")

worst = min(profile, key=lambda row: (-row[2], row[0]))
(out / "summary.json").write_text(
    json.dumps(
        {
            "rows": rows,
            "columns": len(columns),
            "nulls": total_nulls,
            "worst_column": worst[0],
            "worst_nulls": worst[2],
        }
    )
    + "\n",
    encoding="utf-8",
)
