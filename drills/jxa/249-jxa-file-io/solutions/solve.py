#!/usr/bin/env python3
"""249-jxa-file-io — portable reference."""

import csv
import json
import os
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
rows = []
for raw in (inp / "notes.txt").read_text(encoding="utf-8").splitlines():
    text = raw.strip()
    if not text:
        continue
    rows.append((len(rows) + 1, text, len(text), len(text.encode("utf-8"))))

out.mkdir(parents=True, exist_ok=True)
with (out / "lines.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["index", "text", "chars", "bytes"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps(
        {
            "records": len(rows),
            "chars": sum(row[2] for row in rows),
            "bytes": sum(row[3] for row in rows),
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
