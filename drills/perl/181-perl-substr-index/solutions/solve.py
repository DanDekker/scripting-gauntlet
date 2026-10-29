#!/usr/bin/env python3
"""181-perl-substr-index — same contract; find/rfind are the offset tools."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

rows = []
total_pairs = 0

for raw in (IN / "pairs.txt").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    first_eq = line.find("=")
    first = line[:first_eq] if first_eq >= 0 else line
    last_start = line.rfind(";") + 1
    last_eq = line.find("=", last_start)
    last = line[last_start:last_eq] if last_eq >= 0 else ""
    pairs = line.count("=")
    total_pairs += pairs
    second = line.find("=", first_eq + 1) if first_eq >= 0 else -1
    second_eq = second + 1 if second >= 0 else ""
    rows.append((len(rows) + 1, first, last, pairs, second_eq, line[:5]))

with (OUT / "fields.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("line,first,last,pairs,second_eq,head\n")
    for row in rows:
        fh.write(",".join(str(cell) for cell in row) + "\n")

(OUT / "summary.json").write_text(
    json.dumps({"lines": len(rows), "pairs": total_pairs}) + "\n", encoding="utf-8"
)
