#!/usr/bin/env python3
"""Normalize Unix df and Windows Get-Volume snapshots."""

import csv
import json
import os
from pathlib import Path

root = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
rows = []


def read_df(path, platform, mount_field):
    lines = path.read_text(encoding="utf-8").splitlines()
    for line in lines[1:]:
        fields = line.split()
        if len(fields) < mount_field + 1:
            continue
        blocks = int(fields[1])
        available = int(fields[3])
        if blocks <= 0:
            raise SystemExit(f"zero-sized {platform} volume: {' '.join(fields[mount_field:])}")
        mount = " ".join(fields[mount_field:])
        rows.append(
            (platform, mount, blocks * 1024, available * 1024, round(available * 100 / blocks, 1))
        )


read_df(root / "linux/df.txt", "linux", 5)
read_df(root / "macos/df.txt", "macos", 8)
with (root / "windows/volumes.csv").open(newline="", encoding="utf-8") as stream:
    for item in csv.DictReader(stream):
        total = int(item["Size"])
        free = int(item["SizeRemaining"])
        if total <= 0:
            raise SystemExit(f"zero-sized Windows volume: {item['DriveLetter']}")
        volume = f"{item['DriveLetter']}:\\ ({item['FileSystemLabel']})"
        rows.append(("windows", volume, total, free, round(free * 100 / total, 1)))

low = sorted((row for row in rows if row[4] <= 10), key=lambda row: (row[4], row[0], row[1]))
with (out / "low_space.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.writer(stream)
    writer.writerow(["platform", "volume", "total_bytes", "free_bytes", "free_pct"])
    writer.writerows(low)
(out / "summary.json").write_text(
    json.dumps({"volumes_seen": len(rows), "low_space": len(low)}) + "\n", encoding="utf-8"
)
