#!/usr/bin/env python3
"""221-perl-printf-list — python twin."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

records = []
for line in (IN / "records.txt").read_text(encoding="utf-8").splitlines():
    if not line:
        continue
    records.append(line)

lines = 0
with (OUT / "report.txt").open("w", encoding="utf-8", newline="") as fh:
    for record in records:
        fh.write(f"{record}\n")
        lines += 1

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "records": len(records),
            "lines": lines,
            "last": records[-1] if records else "",
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
