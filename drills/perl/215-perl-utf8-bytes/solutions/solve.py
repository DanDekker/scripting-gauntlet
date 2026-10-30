#!/usr/bin/env python3
"""215-perl-utf8-bytes — python twin (text mode decodes; writing encodes back)."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

names = []
for line in (IN / "names.txt").read_text(encoding="utf-8").splitlines():
    if not line:
        continue
    names.append(line)

total = 0
longest = 0

with (OUT / "names.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("index,name,chars\n")
    for index, name in enumerate(names, start=1):
        chars = len(name)
        total += chars
        longest = max(longest, chars)
        fh.write(f"{index},{name.upper()},{chars}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {"names": len(names), "chars": total, "longest": longest},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
