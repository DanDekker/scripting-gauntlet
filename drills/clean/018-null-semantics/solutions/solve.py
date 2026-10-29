#!/usr/bin/env python3
"""018-null-semantics — the token list is the whole job."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

NULL_TOKENS = {"", "na", "n/a", "null", "-"}

with (inp / "people.csv").open(newline="", encoding="utf-8") as fh:
    rows = list(csv.reader(fh))

header, data = rows[0], rows[1:]
nulls = 0
clean = [header]
for row in data:
    converted = []
    for cell in row:
        if cell.strip().lower() in NULL_TOKENS:
            converted.append("")
            nulls += 1
        else:
            converted.append(cell)
    clean.append(converted)

with (out / "clean.csv").open("w", newline="", encoding="utf-8") as fh:
    csv.writer(fh, lineterminator="\n").writerows(clean)

(out / "summary.json").write_text(
    json.dumps({"rows": len(data), "nulls": nulls}) + "\n", encoding="utf-8"
)
