#!/usr/bin/env python3
"""053-fd-limits — count descriptor rows per pid, flag at or over the limit."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

limit = None
for line in (inp / "fd-limit.txt").read_text(encoding="utf-8").splitlines():
    if line.lstrip().startswith("#") or not line.strip():
        continue
    for token in line.split():
        if token.isdigit():
            limit = int(token)
            break
    if limit is not None:
        break
if limit is None:
    raise SystemExit("no integer limit in fd-limit.txt")

counts: dict[int, int] = {}
descriptors = 0
for line in (inp / "fd-listing.txt").read_text(encoding="utf-8").splitlines():
    fields = line.split()
    if not fields or not fields[0].isdigit():
        continue
    counts[int(fields[0])] = counts.get(int(fields[0]), 0) + 1
    descriptors += 1

with (out / "fd-counts.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("pid,descriptors\n")
    for pid, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        fh.write(f"{pid},{count}\n")

flagged = sorted(pid for pid, count in counts.items() if count >= limit)
with (out / "flagged.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("pid,descriptors,limit\n")
    for pid in flagged:
        fh.write(f"{pid},{counts[pid]},{limit}\n")

summary = {
    "processes": len(counts),
    "descriptors": descriptors,
    "limit": limit,
    "flagged": len(flagged),
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
