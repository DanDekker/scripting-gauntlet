#!/usr/bin/env python3
"""014-logfmt — shlex tokenizes the record; the rest is bookkeeping."""

import csv
import json
import os
import shlex
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

rows = []
counts = {"info": 0, "warn": 0, "error": 0}

for line in (inp / "app.log").read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    fields = dict(token.split("=", 1) for token in shlex.split(line))
    duration = int(fields["dur"].removesuffix("ms"))
    rows.append((fields["path"], int(fields["status"]), duration))
    level = fields.get("level", "")
    if level in counts:
        counts[level] += 1

rows.sort(key=lambda row: (-row[2], row[0]))

with (out / "requests.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["path", "status", "dur_ms"])
    writer.writerows(rows)

summary = {
    "lines": len(rows),
    "errors": counts["error"],
    "warns": counts["warn"],
    "infos": counts["info"],
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
