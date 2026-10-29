#!/usr/bin/env python3
"""038-hash-dedup-tree — group by content hash, keep the shortest path, price the waste."""

import csv
import hashlib
import json
import os
from pathlib import Path

tree = Path(os.environ["IN"]) / "tree"
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

groups = {}
files = 0
empty = 0
for path in sorted(tree.rglob("*")):
    if not path.is_file():
        continue
    files += 1
    data = path.read_bytes()
    if not data:  # zero-byte files are never duplicates
        empty += 1
        continue
    rel = path.relative_to(tree).as_posix()
    groups.setdefault(hashlib.sha256(data).hexdigest(), []).append((rel, len(data)))

rows = []
for digest, members in groups.items():
    keeper = min(members, key=lambda member: (len(member[0]), member[0]))[0]
    for name, size in members:
        if name != keeper:
            rows.append((keeper, name, digest, size))
rows.sort(key=lambda row: (row[0], row[1]))

with (out / "dupes.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["keeper", "duplicate", "sha256", "bytes"])
    writer.writerows(rows)

summary = {
    "files": files,
    "unique_hashes": len(groups),
    "duplicate_files": len(rows),
    "wasted_bytes": sum(row[3] for row in rows),
    "empty": empty,
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
