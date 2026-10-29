#!/usr/bin/env python3
"""020-date-parsing — try six shapes, keep the first that is a real date."""

import csv
import json
import os
import re
from datetime import datetime
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

STAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T")
SHAPES = ("%Y-%m-%d", "%m/%d/%Y", "%Y%m%d", "%d %B %Y", "%b %d %Y")


def parse(raw: str) -> str:
    text = raw.strip()
    if STAMP.match(text):
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            return ""
    for shape in SHAPES:
        try:
            return datetime.strptime(text, shape).date().isoformat()
        except ValueError:
            continue
    return ""


rows = []
parsed = failed = 0
dates: list[str] = []
with (inp / "dates.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    next(reader, None)
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        rid, raw = (row + [""] * 2)[:2]
        day = parse(raw)
        if day:
            parsed += 1
            dates.append(day)
        else:
            failed += 1
        rows.append((rid.strip(), day))

with (out / "normalised.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["id", "date"])
    writer.writerows(rows)

summary = {
    "rows": len(rows),
    "parsed": parsed,
    "failed": failed,
    "earliest": min(dates) if dates else "",
    "latest": max(dates) if dates else "",
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
