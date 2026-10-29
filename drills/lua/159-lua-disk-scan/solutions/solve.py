#!/usr/bin/env python3
"""159-lua-disk-scan — same contract; sizes come from the filesystem."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])
ROOT = IN / "tree"


def excluded(segment: str) -> bool:
    return segment == "node_modules" or segment.startswith(".")


stats: dict[str, list[int]] = {}
skipped: set[str] = set()
files = 0
total = 0

for path in sorted(ROOT.rglob("*")):
    if path.is_symlink() or not path.is_file():
        continue
    rel = path.relative_to(ROOT)
    parts = rel.parts
    base = parts[-1]

    excluded_dir = None
    for index in range(len(parts) - 1):
        if excluded(parts[index]):
            excluded_dir = "/".join(parts[: index + 1])
            break
    if excluded_dir is not None:
        skipped.add(excluded_dir)
        continue

    size = path.stat().st_size
    name, dot, suffix = base.rpartition(".")
    ext = suffix.lower() if dot and name else ""
    entry = stats.setdefault(ext, [0, 0])
    entry[0] += 1
    entry[1] += size
    files += 1
    total += size

order = sorted(stats, key=lambda ext: (-stats[ext][1], ext.encode()))

with (OUT / "bytes.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("ext,count,bytes\n")
    for ext in order:
        fh.write(f"{ext},{stats[ext][0]},{stats[ext][1]}\n")

(OUT / "summary.json").write_text(
    json.dumps({"files": files, "bytes": total, "dirs_skipped": len(skipped)}) + "\n",
    encoding="utf-8",
)
