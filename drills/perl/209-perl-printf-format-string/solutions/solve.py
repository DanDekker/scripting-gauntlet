#!/usr/bin/env python3
"""209-perl-printf-format-string — python twin."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

templates = []
for line in (IN / "templates.txt").read_text(encoding="utf-8").splitlines():
    templates.append(line)

with (OUT / "report.txt").open("w", encoding="utf-8", newline="") as fh:
    for template in templates:
        fh.write(f"{template}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "templates": len(templates),
            "percent_templates": sum(1 for t in templates if "%" in t),
            "chars": sum(len(t) for t in templates),
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
