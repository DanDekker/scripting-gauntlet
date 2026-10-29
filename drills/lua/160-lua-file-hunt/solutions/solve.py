#!/usr/bin/env python3
"""160-lua-file-hunt — same contract; fnmatch does the glob translation."""

import fnmatch
import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])
ROOT = IN / "hunt"
GLOB = "*.log"
MIN_BYTES = 100


def excluded(segment: str) -> bool:
    return segment == "archive" or segment.startswith(".")


found: list[tuple[str, int]] = []
scanned = 0
total = 0

for path in sorted(ROOT.rglob("*")):
    if path.is_symlink() or not path.is_file():
        continue
    rel = path.relative_to(ROOT)
    parts = rel.parts
    if any(excluded(part) for part in parts[:-1]):
        continue
    scanned += 1
    size = path.stat().st_size
    if fnmatch.fnmatchcase(parts[-1], GLOB) and size >= MIN_BYTES:
        found.append((rel.as_posix(), size))
        total += size

found.sort(key=lambda row: (-row[1], row[0].encode()))

with (OUT / "found.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("path,size\n")
    for name, size in found:
        fh.write(f"{name},{size}\n")

(OUT / "summary.json").write_text(
    json.dumps({"matched": len(found), "bytes": total, "scanned": scanned}) + "\n",
    encoding="utf-8",
)
