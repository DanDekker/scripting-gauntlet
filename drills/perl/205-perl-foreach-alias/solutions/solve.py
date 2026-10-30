#!/usr/bin/env python3
"""205-perl-foreach-alias — python twin (lists are copied by assignment)."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

names = []
for line in (IN / "names.txt").read_text(encoding="utf-8").splitlines(keepends=True):
    names.append(line.rstrip("\n"))

work = list(names)
for index, name in enumerate(work):
    work[index] = name.strip()[:1].upper() + name.strip()[1:]

changed = sum(1 for original, normalized in zip(names, work) if original != normalized)

with (OUT / "normalized.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("index,name\n")
    for index, name in enumerate(work, start=1):
        fh.write(f"{index},{name}\n")

with (OUT / "original.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("index,name\n")
    for index, name in enumerate(names, start=1):
        fh.write(f"{index},{name}\n")

(OUT / "summary.json").write_text(
    json.dumps({"names": len(names), "changed": changed}, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
