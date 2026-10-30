#!/usr/bin/env python3
"""246-ps1-literal-path — portable reference."""

import csv
import json
import os
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
root = inp / "tree"
rows = []
total_bytes = 0
with (inp / "manifest.csv").open(newline="", encoding="utf-8") as fh:
    for source in csv.DictReader(fh):
        relative = source["path"].strip()
        path = root / relative
        data = path.read_bytes()
        first_line = data.decode("utf-8").splitlines()[0].strip()
        rows.append((relative, len(data), first_line))
        total_bytes += len(data)

out.mkdir(parents=True, exist_ok=True)
with (out / "inventory.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["path", "bytes", "first_line"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps({"files": len(rows), "bytes": total_bytes}, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
