#!/usr/bin/env python3
"""233-perl-cron-schedule — python twin."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

target = {}
for line in (IN / "target.ini").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    k, _, v = line.partition("=")
    target[k.strip()] = int(v.strip())


def match_field(spec: str, val: int) -> bool:
    if spec == "*":
        return True
    if spec.startswith("*/"):
        step = int(spec[2:])
        return val % step == 0
    for part in spec.split(","):
        if "-" in part:
            lo, hi = map(int, part.split("-"))
            if lo <= val <= hi:
                return True
        elif part.isdigit() and int(part) == val:
            return True
    return False


matched = []
total = 0

for line in (IN / "crontab.txt").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    total += 1
    parts = line.split(None, 5)
    f_min, f_hour, f_dom, f_mon, f_dow, cmd = parts

    if (
        match_field(f_min, target["minute"])
        and match_field(f_hour, target["hour"])
        and match_field(f_dom, target["dom"])
        and match_field(f_mon, target["month"])
        and match_field(f_dow, target["dow"])
    ):
        matched.append(cmd)

(OUT / "matched.txt").write_text(
    "".join(f"{cmd}\n" for cmd in matched), encoding="utf-8"
)

(OUT / "summary.json").write_text(
    json.dumps(
        {"total_entries": total, "matched": len(matched)},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
