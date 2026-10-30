#!/usr/bin/env python3
"""206-perl-exists-autoviv — python twin (dict lookups do not create entries)."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

cfg: dict[str, dict[str, str]] = {}
section = None
for raw in (IN / "base.conf").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    if line.startswith("[") and line.endswith("]"):
        section = line[1:-1]
        cfg.setdefault(section, {})
        continue
    if section is None:
        continue
    key, _, value = line.partition("=")
    cfg[section][key] = value

rows = []
present_count = 0
for raw in (IN / "wanted.conf").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    wanted_section, _, key = line.partition(".")
    index = len(rows) + 1
    present = wanted_section in cfg and key in cfg[wanted_section]
    if present:
        present_count += 1
    rows.append((index, wanted_section, key, "present" if present else "missing"))

with (OUT / "missing.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("index,section,key,status\n")
    for row in rows:
        fh.write(f"{row[0]},{row[1]},{row[2]},{row[3]}\n")

with (OUT / "dump.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("section,keys\n")
    for name in sorted(cfg):
        fh.write(f"{name},{len(cfg[name])}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "wanted": len(rows),
            "present": present_count,
            "missing": len(rows) - present_count,
            "sections": len(cfg),
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
