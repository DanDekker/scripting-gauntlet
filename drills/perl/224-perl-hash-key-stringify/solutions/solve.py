#!/usr/bin/env python3
"""224-perl-hash-key-stringify — python twin (dict keys are the text read)."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

inventory = {}
for line in (IN / "inventory.txt").read_text(encoding="utf-8").splitlines():
    if not line:
        continue
    key, _, name = line.partition(" ")
    inventory[key] = name

lookups = [
    line
    for line in (IN / "lookups.txt").read_text(encoding="utf-8").splitlines()
    if line
]

rows = []
hits = 0
misses = 0
for index, lookup in enumerate(lookups, start=1):
    if lookup in inventory:
        hits += 1
        rows.append((index, lookup, "hit", inventory[lookup]))
    else:
        misses += 1
        rows.append((index, lookup, "miss", ""))

with (OUT / "lookups.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("index,lookup,status,name\n")
    for row in rows:
        fh.write(f"{row[0]},{row[1]},{row[2]},{row[3]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {"lookups": len(rows), "hits": hits, "misses": misses},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
