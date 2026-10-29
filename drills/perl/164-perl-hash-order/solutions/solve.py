#!/usr/bin/env python3
"""164-perl-hash-order — same contract; dict order is insertion, so sort explicitly."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

counts: dict[str, int] = {}
events = invalid = 0

for raw in (IN / "events.log").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    fields = line.split()
    if len(fields) < 2:
        invalid += 1
        continue
    counts[fields[0]] = counts.get(fields[0], 0) + 1
    events += 1

order = sorted(counts, key=lambda user: (-counts[user], user.encode()))

with (OUT / "counts.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("user,events\n")
    for user in order:
        fh.write(f"{user},{counts[user]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "users": len(order),
            "events": events,
            "invalid": invalid,
            "top": order[0] if order else "",
        }
    )
    + "\n",
    encoding="utf-8",
)
