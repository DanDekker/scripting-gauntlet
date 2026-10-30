#!/usr/bin/env python3
"""258-tcl-file-literal — portable reference."""

import csv
import json
import os
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
root = inp / "tree"
rows = []
for relative in (inp / "manifest.txt").read_text(encoding="utf-8").splitlines():
    relative = relative.strip()
    if not relative:
        continue
    path = root / relative
    data = path.read_bytes()
    rows.append((relative, len(data), data.decode("utf-8").splitlines()[0].strip()))

out.mkdir(parents=True, exist_ok=True)
with (out / "files.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["path", "bytes", "first_line"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps({"files": len(rows), "bytes": sum(row[1] for row in rows)}, separators=(",", ":"))
    + "\n",
    encoding="utf-8",
)
