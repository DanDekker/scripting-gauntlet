#!/usr/bin/env python3
"""072-cron-expand - five fields, five ranges, one expander."""

import json
import os
import re
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

MONTHS = {name: i for i, name in enumerate(
    "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split(), start=1)}
WEEKDAYS = {name: i for i, name in enumerate("SUN MON TUE WED THU FRI SAT".split())}

FIELDS = [
    ("minute", 0, 59, None),
    ("hour", 0, 23, None),
    ("dom", 1, 31, None),
    ("month", 1, 12, MONTHS),
    ("dow", 0, 7, WEEKDAYS),
]


class BadField(ValueError):
    pass


def number(token: str, names: dict[str, int] | None) -> int:
    if names is not None and token.upper() in names:
        return names[token.upper()]
    if re.fullmatch(r"[0-9]+", token):
        return int(token)
    raise BadField(token)


def expand(spec: str, low: int, high: int, names) -> list[int]:
    seen: set[int] = set()
    for item in spec.split(","):
        step = 1
        body = item
        if "/" in item:
            body, _, raw_step = item.partition("/")
            if not re.fullmatch(r"[0-9]+", raw_step) or int(raw_step) < 1:
                raise BadField(item)
            step = int(raw_step)
        if body == "*":
            low_value, high_value = low, high
        elif "-" in body:
            first, _, last = body.partition("-")
            low_value, high_value = number(first, names), number(last, names)
        else:
            low_value = high_value = number(body, names)
        if low_value > high_value:
            raise BadField(item)
        for value in range(low_value, high_value + 1, step):
            seen.add(value)
    if not seen:
        raise BadField(spec)
    values = sorted(v for v in seen if v <= 6) if high == 7 else sorted(seen)
    if high == 7 and 7 in seen:
        values = sorted(set(values) | {0})
    return values


schedule = {}
slots = 0
with (inp / "jobs.txt").open(encoding="utf-8") as fh:
    for lineno, raw in enumerate(fh, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None)
        if len(parts) != 6:
            raise SystemExit(f"line {lineno}: expected job plus 5 fields: {line}")
        job, specs = parts[0], parts[1:]
        if not re.fullmatch(r"[a-z0-9_-]+", job):
            raise SystemExit(f"line {lineno}: bad job name {job!r}")
        entry = {}
        for (name, low, high, names), spec in zip(FIELDS, specs):
            try:
                entry[name] = expand(spec, low, high, names)
            except BadField:
                raise SystemExit(f"{job}: bad {name} field: {spec}")
        schedule[job] = entry
        slots += len(entry["minute"]) * len(entry["hour"])

(out / "schedule.json").write_text(json.dumps(schedule, indent=2) + "\n", encoding="utf-8")
summary = {"jobs": len(schedule), "slots": slots}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
