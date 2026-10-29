#!/usr/bin/env python3
"""040-extract-column — read the header, keep the index, print that field."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

hosts, skipped, col = [], 0, None
with (inp / "servers.csv").open(newline="", encoding="utf-8") as fh:
    for index, row in enumerate(csv.reader(fh)):
        if index == 0:
            header = [cell.strip() for cell in row]
            if "host" not in header:
                raise SystemExit("servers.csv: no host column in header")
            col = header.index("host")
            continue
        if not any(cell.strip() for cell in row):
            skipped += 1
            continue
        if row[0].strip().startswith("#"):
            skipped += 1
            continue
        hosts.append(row[col].strip())

with (out / "hosts.txt").open("w", encoding="utf-8", newline="") as fh:
    fh.write("".join(f"{host}\n" for host in hosts))

(out / "summary.json").write_text(
    json.dumps({"rows": len(hosts), "skipped": skipped}) + "\n", encoding="utf-8"
)
