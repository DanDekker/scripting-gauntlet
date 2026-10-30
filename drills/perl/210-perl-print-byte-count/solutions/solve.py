#!/usr/bin/env python3
"""210-perl-print-byte-count — python twin."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

items = []
for line in (IN / "items.txt").read_text(encoding="utf-8").splitlines():
    items.append(line)

report = ""
for item in items:
    report += item + "\n"
(OUT / "report.txt").write_bytes(report.encode("utf-8"))

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "items": len(items),
            "bytes": len(report.encode("utf-8")),
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
