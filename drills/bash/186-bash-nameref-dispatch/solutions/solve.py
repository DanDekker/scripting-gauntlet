#!/usr/bin/env python3
"""186-bash-nameref-dispatch — python twin with identical contract."""

import json
import os
from collections import defaultdict
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

buckets: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
categories_seen = set()

for line in (IN / "actions.txt").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    parts = line.split()
    if len(parts) != 3:
        continue
    cat, metric, amount_str = parts
    amt = int(amount_str)
    buckets[cat][metric] += amt
    categories_seen.add(cat)

rows = []
total_sum = 0
for cat in sorted(buckets.keys()):
    for metric in sorted(buckets[cat].keys()):
        val = buckets[cat][metric]
        rows.append((cat, metric, str(val)))
        total_sum += val

with (OUT / "tallies.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("category,metric,total\n")
    for r in rows:
        fh.write(",".join(r) + "\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "categories": len(buckets),
            "entries": len(rows),
            "total": total_sum,
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
