#!/usr/bin/env python3
"""024-dedupe-exact — trim into a tuple key, keep the first hit, never sort."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

rows_in = 0
dropped = 0
unique: list[list[str]] = []
seen: set[tuple[str, ...]] = set()

with (inp / "signups.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    next(reader, None)
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        rows_in += 1
        fields = tuple(cell.strip() for cell in (row + [""] * 4)[:4])
        if fields in seen:
            dropped += 1
            continue
        seen.add(fields)
        unique.append(list(fields))

with (out / "deduped.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["email", "name", "plan", "signed_up"])
    writer.writerows(unique)

summary = {"rows_in": rows_in, "unique": len(unique), "dropped": dropped}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
