#!/usr/bin/env python3
"""163-perl-literal-match — same contract; str.find is the literal search."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

rows = []
lines = matched = invalid = 0

for raw in (IN / "queries.txt").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    if "|" not in line:
        invalid += 1
        continue
    pattern, _, subject = line.partition("|")
    pattern = pattern.strip()
    subject = subject.strip()
    lines += 1

    first = subject.find(pattern) if pattern else -1
    count = 0
    at = 0
    while pattern:
        found_at = subject.find(pattern, at)
        if found_at < 0:
            break
        count += 1
        at = found_at + len(pattern)  # non-overlapping
    if first >= 0:
        matched += 1
        rows.append((pattern, 1, first + 1, count))
    else:
        rows.append((pattern, 0, "", count))

with (OUT / "matches.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("pattern,found,position,count\n")
    for row in rows:
        fh.write(",".join(str(cell) for cell in row) + "\n")

(OUT / "summary.json").write_text(
    json.dumps({"lines": lines, "matched": matched, "invalid": invalid}) + "\n",
    encoding="utf-8",
)
