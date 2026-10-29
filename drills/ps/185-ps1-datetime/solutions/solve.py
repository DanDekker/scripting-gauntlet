#!/usr/bin/env python3
"""185-ps1-datetime — same contract; explicit strptime patterns and a UTC calendar."""

import calendar
import csv
import json
import os
from datetime import datetime
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

ISO = "%Y-%m-%dT%H:%M:%SZ"
EU = "%d/%m/%Y"

rows = []
invalid = 0

with (IN / "stamps.csv").open(newline="", encoding="utf-8") as fh:
    for record in csv.DictReader(fh):
        stamp = record["stamp"].strip()
        moment = None
        for pattern in (ISO, EU):
            try:
                moment = datetime.strptime(stamp, pattern)
                break
            except ValueError:
                continue
        if moment is None:
            invalid += 1
            continue
        rows.append((int(record["id"]), calendar.timegm(moment.timetuple())))

rows.sort(key=lambda row: row[0])

with (OUT / "epochs.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("id,epoch\n")
    for rid, epoch in rows:
        fh.write(f"{rid},{epoch}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "rows": len(rows),
            "invalid": invalid,
            "earliest": min((epoch for _rid, epoch in rows), default=""),
        }
    )
    + "\n",
    encoding="utf-8",
)
