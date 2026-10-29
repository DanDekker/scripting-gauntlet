#!/usr/bin/env python3
"""153-lua-sort-ties — same contract, explicit index tie-break."""

import json
import os
import re
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

LINE_RE = re.compile(r"^(\S+)\s+(\d+)$")

records: list[tuple[str, int, int]] = []
invalid = 0

for raw in (IN / "scores.txt").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    match = LINE_RE.match(line)
    if not match:
        invalid += 1
        continue
    records.append((match.group(1), int(match.group(2)), len(records) + 1))

records.sort(key=lambda record: (-record[1], record[2]))

with (OUT / "sorted.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("name,score,index\n")
    for name, score, index in records:
        fh.write(f"{name},{score},{index}\n")

counts: dict[int, int] = {}
for _, score, _ in records:
    counts[score] = counts.get(score, 0) + 1

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "records": len(records),
            "invalid": invalid,
            "tied": sum(1 for _, score, _ in records if counts[score] > 1),
        }
    )
    + "\n",
    encoding="utf-8",
)
