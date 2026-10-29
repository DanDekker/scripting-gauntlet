#!/usr/bin/env python3
"""188-perl-context-dispatch — python twin with identical contract."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

records = []
for line in (IN / "records.txt").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    parts = line.split()
    records.append({"id": parts[0], "score": int(parts[1]), "label": parts[2]})


def filter_scores(threshold, context="list"):
    matches = [r["id"] for r in records if r["score"] >= threshold]
    if context == "scalar":
        return str(len(matches))
    elif context == "list":
        return ";".join(matches)
    elif context == "list_first":
        return matches[0] if matches else ""
    return ""


rows = [
    (1, "scalar", filter_scores(70, "scalar")),
    (2, "list", filter_scores(70, "list")),
    (3, "list_first", filter_scores(70, "list_first")),
    (4, "scalar", filter_scores(90, "scalar")),
]

with (OUT / "dispatches.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("caller,context,result\n")
    for r in rows:
        fh.write(f"{r[0]},{r[1]},{r[2]}\n")

(OUT / "summary.json").write_text(
    json.dumps({"queries": 4, "list_queries": 2, "scalar_queries": 2}, separators=(",", ":"))
    + "\n",
    encoding="utf-8",
)
