#!/usr/bin/env python3
"""151-lua-exact-decimals — same contract, integer arithmetic only."""

import json
import os
import re
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

VALUE_RE = re.compile(r"^([+-]?)(\d+)(?:\.(\d{1,3}))?$")


def to_thousandths(text: str):
    match = VALUE_RE.match(text)
    if not match:
        return None
    sign, whole, frac = match.group(1), match.group(2), match.group(3) or ""
    value = int(whole) * 1000 + int(frac.ljust(3, "0"))
    return -value if sign == "-" else value


def scaled(value: int) -> str:
    sign = "-" if value < 0 else ""
    value = abs(value)
    return f"{sign}{value // 1000}.{value % 1000:03d}"


stats: dict[str, dict] = {}
records = 0
invalid = 0

for index, raw in enumerate((IN / "measurements.csv").read_text(encoding="utf-8").splitlines()):
    if index == 0:
        continue
    line = raw.strip()
    if not line:
        continue
    sensor, _, value = line.partition(",")
    sensor = sensor.strip()
    value = value.strip()
    scaled_value = to_thousandths(value) if sensor else None
    if scaled_value is None:
        invalid += 1
        continue
    records += 1
    entry = stats.setdefault(sensor, {"count": 0, "min": scaled_value, "max": scaled_value, "total": 0})
    entry["count"] += 1
    entry["total"] += scaled_value
    entry["min"] = min(entry["min"], scaled_value)
    entry["max"] = max(entry["max"], scaled_value)

with (OUT / "sensors.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("sensor,count,min,max,total\n")
    for sensor in sorted(stats, key=lambda s: s.encode()):
        entry = stats[sensor]
        fh.write(
            f"{sensor},{entry['count']},{scaled(entry['min'])},"
            f"{scaled(entry['max'])},{scaled(entry['total'])}\n"
        )

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "sensors": len(stats),
            "records": records,
            "invalid": invalid,
            "total": scaled(sum(entry["total"] for entry in stats.values())),
        }
    )
    + "\n",
    encoding="utf-8",
)
