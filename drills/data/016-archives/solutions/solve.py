#!/usr/bin/env python3
"""016-archives — gzip and tarfile, both read straight into memory."""

import csv
import gzip
import io
import json
import os
import tarfile
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

sources = 0
rows = []

for path in sorted(inp.glob("*.tar.gz")):
    sources += 1
    with tarfile.open(path, "r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile() or not member.name.endswith(".csv"):
                continue
            payload = tar.extractfile(member)
            if payload is None:
                continue
            text = payload.read().decode("utf-8")
            for row in list(csv.reader(io.StringIO(text)))[1:]:
                if row:
                    rows.append((row[1], float(row[2])))

for path in sorted(inp.glob("*.csv.gz")):
    sources += 1
    with gzip.open(path, "rb") as fh:
        text = fh.read().decode("utf-8")
    for row in list(csv.reader(io.StringIO(text)))[1:]:
        if row:
            rows.append((row[1], float(row[2])))

totals: dict[str, list] = {}
for region, amount in rows:
    bucket = totals.setdefault(region, [0.0, 0])
    bucket[0] += amount
    bucket[1] += 1

with (out / "by_region.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["region", "amount", "rows"])
    for region, (amount, count) in sorted(totals.items(), key=lambda kv: (-kv[1][0], kv[0])):
        writer.writerow([region, f"{amount:.2f}", count])

(out / "summary.json").write_text(
    json.dumps({"files": sources, "rows": len(rows)}) + "\n", encoding="utf-8"
)
