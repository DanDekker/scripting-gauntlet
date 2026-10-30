#!/usr/bin/env python3
"""225-perl-die-message — python twin (the caught text is the message, unadorned)."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

checks = []
for line in (IN / "checks.txt").read_text(encoding="utf-8").splitlines():
    if not line:
        continue
    name, _, message = line.partition(" ")
    checks.append((name, message))

rows = []
longest = 0
first = ""
for index, (name, message) in enumerate(checks, start=1):
    try:
        raise RuntimeError(message)
    except RuntimeError as exc:
        caught = str(exc)
    longest = max(longest, len(caught))
    if index == 1:
        first = caught
    rows.append((index, name, caught))

with (OUT / "checks.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("index,name,message\n")
    for row in rows:
        fh.write(f"{row[0]},{row[1]},{row[2]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {"checks": len(rows), "longest": longest, "first": first},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
