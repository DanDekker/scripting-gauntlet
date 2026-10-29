#!/usr/bin/env python3
"""157-lua-needle-haystack — same contract, bytes in and strings out."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

NEEDLE = "token=100%".encode()
ROOT = IN / "corpus"

files = []
binary = 0

for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or path.is_symlink():
        continue
    blob = path.read_bytes()
    if b"\x00" in blob:
        binary += 1
        continue
    files.append((path.relative_to(ROOT).as_posix(), blob))

hits = []
for name, blob in files:
    for number, line in enumerate(blob.split(b"\n")[:-1], start=1):
        column = line.find(NEEDLE)
        if column != -1:
            hits.append((name, number, column + 1))

hits.sort(key=lambda row: (row[0].encode(), row[1]))

with (OUT / "hits.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("path,line,column\n")
    for name, number, column in hits:
        fh.write(f"{name},{number},{column}\n")

(OUT / "summary.json").write_text(
    json.dumps({"files": len(files), "binary": binary, "hits": len(hits)}) + "\n",
    encoding="utf-8",
)
