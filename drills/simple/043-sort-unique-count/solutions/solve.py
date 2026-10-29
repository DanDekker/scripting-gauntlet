#!/usr/bin/env python3
"""043-sort-unique-count — normalize into a Counter, sort the items."""

import json
import os
from collections import Counter
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

counts = Counter()
lines = 0
with (inp / "app.log").open(encoding="utf-8") as fh:
    for line in fh:
        fields = line.split()
        if not fields:
            continue
        lines += 1
        counts[fields[1].upper()] += 1

rows = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
with (out / "levels.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("level,count\n")
    for level, count in rows:
        fh.write(f"{level},{count}\n")

(out / "summary.json").write_text(
    json.dumps(
        {
            "lines": lines,
            "levels": len(counts),
            "top": rows[0][0] if rows else "",
        }
    )
    + "\n",
    encoding="utf-8",
)
