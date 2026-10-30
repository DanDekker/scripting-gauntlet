#!/usr/bin/env python3
"""217-perl-reverse-context — python twin."""

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

reversed_records = list(reversed(records))

with (OUT / "records.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("index,record\n")
    for index, record in enumerate(reversed_records, start=1):
        fh.write(f"{index},{record}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "records": len(records),
            "first": reversed_records[0] if reversed_records else "",
            "last": reversed_records[-1] if reversed_records else "",
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
