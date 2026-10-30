#!/usr/bin/env python3
"""251-jxa-date-timezone — portable reference."""

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
rows = []
rejected = 0
epoch_zero = 0
with (inp / "stamps.csv").open(newline="", encoding="utf-8") as fh:
    for source in csv.DictReader(fh):
        try:
            date = datetime.fromisoformat(source["stamp"].replace("Z", "+00:00"))
            if date.tzinfo is None:
                raise ValueError("offset required")
        except ValueError:
            rejected += 1
            continue
        utc = date.astimezone(timezone.utc)
        epoch = int(utc.timestamp())
        epoch_zero += epoch == 0
        rows.append((source["id"], utc.strftime("%Y-%m-%dT%H:%M:%SZ"), epoch))

out.mkdir(parents=True, exist_ok=True)
with (out / "stamps.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["id", "utc", "epoch"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps({"accepted": len(rows), "rejected": rejected, "epoch_zero": epoch_zero}, separators=(",", ":"))
    + "\n",
    encoding="utf-8",
)
