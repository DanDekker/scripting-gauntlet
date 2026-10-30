#!/usr/bin/env python3
"""260-tcl-catch-expr — portable reference."""

import csv
import json
import os
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
rows = []
rejected = 0
with (inp / "ratios.csv").open(newline="", encoding="utf-8") as fh:
    for source in csv.DictReader(fh):
        try:
            numerator = float(source["numerator"])
            denominator = float(source["denominator"])
            if denominator == 0:
                raise ValueError("zero denominator")
            ratio = numerator / denominator
        except ValueError:
            rejected += 1
            continue
        rows.append((source["id"], f"{ratio:.2f}"))

out.mkdir(parents=True, exist_ok=True)
with (out / "ratios.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["id", "ratio"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps({"accepted": len(rows), "rejected": rejected}, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
