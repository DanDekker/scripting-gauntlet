#!/usr/bin/env python3
"""084-fd-leak - slope per minute, monotonicity, and a measured threshold."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

series: dict[int, list[tuple[int, int]]] = {}
for lineno, raw in enumerate((inp / "fd-samples.csv").read_text(encoding="utf-8").splitlines(), 1):
    line = raw.strip()
    if not line or line.startswith("sample"):
        continue
    fields = line.split(",")
    if len(fields) != 3 or not all(part.strip().isdigit() for part in fields):
        raise SystemExit(f"line {lineno}: expected sample,pid,fds")
    sample, pid, fds = (int(part) for part in fields)
    series.setdefault(pid, []).append((sample, fds))

rows = []
skipped = 0
for pid, samples in series.items():
    samples.sort()
    if len(samples) < 2:
        skipped += 1
        continue
    first_sample, first_fds = samples[0]
    last_sample, last_fds = samples[-1]
    rate = (last_fds - first_fds) / (last_sample - first_sample)
    monotonic = all(b >= a for (_, a), (_, b) in zip(samples, samples[1:]))
    rows.append((rate, pid, first_fds, last_fds, monotonic))

rows.sort(key=lambda row: (-row[0], row[1]))
with (out / "leaks.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("pid,first_fds,last_fds,fds_per_min,monotonic\n")
    for rate, pid, first_fds, last_fds, monotonic in rows:
        fh.write(
            f"{pid},{first_fds},{last_fds},{rate:.1f},{'true' if monotonic else 'false'}\n"
        )

summary = {
    "pids": len(rows),
    "leaking": sum(1 for row in rows if row[4] and row[0] >= 5.0),
    "skipped": skipped,
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
