#!/usr/bin/env python3
"""230-perl-ini-config — python twin."""

import csv
import json
import os
import re
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

cfg = {}
cur = "default"

for line in (IN / "config.ini").read_text(encoding="utf-8").splitlines():
    line = re.sub(r"\s*[#;].*", "", line).strip()
    if not line:
        continue
    m_sec = re.match(r"^\[(\w+)\]$", line)
    if m_sec:
        cur = m_sec.group(1)
        continue
    m_kv = re.match(r"^(\w+)\s*=\s*(.+)$", line)
    if m_kv:
        cfg.setdefault(cur, {})[m_kv.group(1)] = m_kv.group(2).strip()

rows = []
counts = {"section": 0, "default": 0, "none": 0}

with (IN / "queries.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    next(reader, None)
    for row in reader:
        if not row:
            continue
        sec, key = row[0].strip(), row[1].strip()
        if sec in cfg and key in cfg[sec]:
            val = cfg[sec][key]
            src = "section"
        elif "default" in cfg and key in cfg["default"]:
            val = cfg["default"][key]
            src = "default"
        else:
            val = "MISSING"
            src = "none"
        counts[src] += 1
        rows.append((sec, key, val, src))

with (OUT / "answers.csv").open("w", encoding="utf-8", newline="") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["section", "key", "value", "source"])
    for r in rows:
        writer.writerow(r)

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "queries": len(rows),
            "section": counts["section"],
            "default": counts["default"],
            "missing": counts["none"],
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
