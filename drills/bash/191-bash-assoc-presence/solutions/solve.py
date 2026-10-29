#!/usr/bin/env python3
"""191-bash-assoc-presence — python twin with dictionary key membership."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

config = {}
for line in (IN / "config.txt").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    k, _, v = line.partition("=")
    config[k.strip()] = v.strip()

rows = []
counts = {"set": 0, "empty": 0, "missing": 0}

for line in (IN / "queries.txt").read_text(encoding="utf-8").splitlines():
    q = line.strip()
    if not q or q.startswith("#"):
        continue
    if q in config:
        val = config[q]
        if val == "":
            status = "empty"
        else:
            status = "set"
    else:
        status = "missing"
        val = ""
    counts[status] += 1
    rows.append((q, status, val))

with (OUT / "results.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("key,status,value\n")
    for r in rows:
        fh.write(f"{r[0]},{r[1]},{r[2]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "queries": len(rows),
            "set": counts["set"],
            "empty": counts["empty"],
            "missing": counts["missing"],
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
