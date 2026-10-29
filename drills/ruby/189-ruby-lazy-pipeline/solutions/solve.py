#!/usr/bin/env python3
"""189-ruby-lazy-pipeline — python twin with generator pipeline."""

import json
import os
import re
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

inspected = 0
target = 5
matches = []


def stream_lines():
    global inspected
    with (IN / "stream.log").open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            inspected += 1
            yield line


for line in stream_lines():
    if "[payment]" in line and ("WARN" in line or "ERROR" in line):
        parts = line.split(None, 3)
        ts, level = parts[0], parts[1]
        m = re.search(r"code=(\d+)\s*(.*)$", line)
        code = int(m.group(1)) if m else 0
        msg = m.group(2) if m else ""
        matches.append((ts, level, code, msg))
        if len(matches) == target:
            break

with (OUT / "matches.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("timestamp,level,code,message\n")
    for r in matches:
        fh.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {"inspected": inspected, "matched": len(matches), "target": target},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
