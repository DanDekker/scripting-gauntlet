#!/usr/bin/env python3
"""180-perl-substitution-eval — same contract; re.subn returns text and count together."""

import json
import os
import re
from pathlib import Path

PAIR = re.compile(r"(\w+)=(\S*)")

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

rows = []
total = 0

for raw in (IN / "assignments.txt").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    text, count = PAIR.subn(lambda m: f"{m.group(1).upper()}:{m.group(2).upper()}", line)
    total += count
    rows.append((len(rows) + 1, text, count))

with (OUT / "rewritten.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("line,text,substitutions\n")
    for row in rows:
        fh.write(",".join(str(cell) for cell in row) + "\n")

(OUT / "summary.json").write_text(
    json.dumps({"lines": len(rows), "substitutions": total}) + "\n", encoding="utf-8"
)
