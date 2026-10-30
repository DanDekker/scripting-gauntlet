#!/usr/bin/env python3
"""250-jxa-path-inventory — portable reference."""

import csv
import json
import os
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
root = inp / "tree"
rows = []
with (inp / "manifest.txt").open(encoding="utf-8") as fh:
    for raw in fh:
        relative = raw.strip()
        if not relative:
            continue
        path = root / relative
        rows.append((relative, path.stat().st_size, "file"))

out.mkdir(parents=True, exist_ok=True)
with (out / "inventory.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["path", "bytes", "kind"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps({"files": len(rows), "bytes": sum(row[1] for row in rows)}, separators=(",", ":"))
    + "\n",
    encoding="utf-8",
)
