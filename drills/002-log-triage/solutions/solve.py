#!/usr/bin/env python3
"""002-log-triage — one regex per line, then two sorted reports."""

import json
import os
import re
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

RECORD = re.compile(r'"(\S+) (\S+) HTTP/[\d.]+\s*"?\s*(\d{3})\b')

status_counts: dict[str, int] = {}
path_counts: dict[str, int] = {}
valid = skipped = 0

text = (inp / "access.log").read_text(encoding="utf-8", errors="replace")
for line in text.splitlines():
    match = RECORD.search(line)
    if not match:
        skipped += 1
        continue
    _, raw_path, status = match.groups()
    valid += 1
    status_counts[status] = status_counts.get(status, 0) + 1
    path = raw_path.split("?", 1)[0]
    path_counts[path] = path_counts.get(path, 0) + 1

with (out / "status.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("status,count\n")
    for status, count in sorted(status_counts.items(), key=lambda kv: (-kv[1], int(kv[0]))):
        fh.write(f"{status},{count}\n")

with (out / "top_paths.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("path,hits\n")
    for path, hits in sorted(path_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]:
        fh.write(f"{path},{hits}\n")

(out / "summary.json").write_text(
    json.dumps({"valid": valid, "skipped": skipped}) + "\n", encoding="utf-8"
)
