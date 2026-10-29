#!/usr/bin/env python3
"""039-count-lines — count records, not newlines."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

counts = []
for path in sorted(inp.glob("*.log")):
    text = path.read_bytes().decode("utf-8", "replace")
    # a trailing record without a newline is still a line
    counts.append((path.name, text.count("\n") + (1 if text and not text.endswith("\n") else 0)))

with (out / "linecounts.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("file,lines\n")
    for name, n in counts:
        fh.write(f"{name},{n}\n")

(out / "total.json").write_text(
    json.dumps({"files": len(counts), "lines": sum(n for _, n in counts)}) + "\n",
    encoding="utf-8",
)
