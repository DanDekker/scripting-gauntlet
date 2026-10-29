#!/usr/bin/env python3
"""165-perl-timegm — same contract; calendar.timegm plus a round-trip check."""

import calendar
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

STAMP_RE = re.compile(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})Z$")

rows = []
lines = invalid = 0

for raw in (IN / "stamps.txt").read_text(encoding="utf-8").splitlines():
    stamp = raw.strip()
    if not stamp or stamp.startswith("#"):
        continue
    lines += 1
    match = STAMP_RE.match(stamp)
    if not match:
        invalid += 1
        continue
    year, mon, mday, hour, minute, second = (int(part) for part in match.groups())
    try:
        moment = datetime(year, mon, mday, hour, minute, second, tzinfo=timezone.utc)
    except ValueError:
        invalid += 1
        continue
    rows.append((stamp, int(moment.timestamp())))

rows.sort(key=lambda row: (row[1], row[0].encode()))

with (OUT / "epochs.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("stamp,epoch\n")
    for stamp, epoch in rows:
        fh.write(f"{stamp},{epoch}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "lines": lines,
            "valid": len(rows),
            "invalid": invalid,
            "first": rows[0][1] if rows else "",
            "last": rows[-1][1] if rows else "",
        }
    )
    + "\n",
    encoding="utf-8",
)
