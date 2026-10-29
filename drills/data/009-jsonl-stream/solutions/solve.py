#!/usr/bin/env python3
"""009-jsonl-stream — read the file line by line and fold it."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

by_country: dict[str, list] = {}
tags: dict[str, int] = {}
users: set[str] = set()
events = 0

with (inp / "events.jsonl").open(encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        event = json.loads(line)
        events += 1
        users.add(event["user"]["id"])

        country = event["user"]["country"]
        bucket = by_country.setdefault(country, [0, 0.0])
        bucket[0] += 1
        bucket[1] += event["amount"]

        for tag in event.get("tags", []):
            tags[tag] = tags.get(tag, 0) + 1

with (out / "by_country.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["country", "events", "revenue"])
    for country, (count, revenue) in sorted(by_country.items(), key=lambda kv: (-kv[1][1], kv[0])):
        writer.writerow([country, count, revenue])

with (out / "tags.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["tag", "count"])
    for tag, count in sorted(tags.items(), key=lambda kv: (-kv[1], kv[0])):
        writer.writerow([tag, count])

(out / "summary.json").write_text(
    json.dumps({"events": events, "users": len(users)}) + "\n", encoding="utf-8"
)
