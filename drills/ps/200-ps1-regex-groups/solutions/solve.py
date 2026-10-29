#!/usr/bin/env python3
"""200-ps1-regex-groups — python twin with guarded regex matching."""

import json
import os
import re
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

pattern = re.compile(
    r"^LOG (?P<stamp>\S+) ID=(?P<id>\d+) status=(?P<status>\w+) duration_ms=(?P<dur>\d+)$"
)

rows = []
step = 0
valid_count = 0
corrupt_count = 0
total_dur = 0

for line in (IN / "events.log").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue

    step += 1
    m = pattern.match(line)
    if m:
        valid_count += 1
        rid = int(m.group("id"))
        status = m.group("status")
        dur = int(m.group("dur"))
        total_dur += dur
        valid = "true"
    else:
        corrupt_count += 1
        rid = ""
        status = ""
        dur = ""
        valid = "false"

    rows.append((step, rid, status, dur, valid))

with (OUT / "parsed.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("step,id,status,duration,valid\n")
    for r in rows:
        fh.write(f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]}\n")

avg_dur = int(total_dur / valid_count) if valid_count > 0 else 0
(OUT / "summary.json").write_text(
    json.dumps(
        {
            "total_lines": len(rows),
            "valid_records": valid_count,
            "corrupt_lines": corrupt_count,
            "avg_duration": avg_dur,
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
