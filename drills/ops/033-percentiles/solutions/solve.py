#!/usr/bin/env python3
"""033-percentiles — group, sort each group, read the nearest-rank index."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

samples: dict[str, list[int]] = {}
with (inp / "latency.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    next(reader, None)
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        endpoint, ms = (cell.strip() for cell in (row + [""] * 2)[:2])
        samples.setdefault(endpoint.lower(), []).append(int(ms))


def nearest_rank(values: list[int], percent: int) -> int:
    n = len(values)
    return values[(percent * n + 99) // 100 - 1]


rows = []
for endpoint in sorted(samples):
    values = sorted(samples[endpoint])
    rows.append(
        (
            endpoint,
            len(values),
            nearest_rank(values, 50),
            nearest_rank(values, 90),
            values[-1],
        )
    )

with (out / "latency.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["endpoint", "count", "p50", "p90", "max"])
    writer.writerows(rows)

summary = {
    "endpoints": len(rows),
    "requests": sum(row[1] for row in rows),
    "slowest": max((value for values in samples.values() for value in values), default=0),
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
