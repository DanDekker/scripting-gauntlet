#!/usr/bin/env python3
"""198-perl-state-variables — python twin with stateful closure dictionary."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

streaks = {}


def record_check(svc, status):
    if status == "FAIL":
        streaks[svc] = streaks.get(svc, 0) + 1
    else:
        streaks[svc] = 0
    st = streaks[svc]
    return st, "true" if st >= 3 else "false"


rows = []
step = 0
alerts_count = 0
max_streak = 0

for line in (IN / "checks.log").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    step += 1
    ts, svc, status = line.split()
    streak, alert = record_check(svc, status)
    if alert == "true":
        alerts_count += 1
    if streak > max_streak:
        max_streak = streak
    rows.append((step, ts, svc, status, streak, alert))

with (OUT / "streaks.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("step,timestamp,service,status,streak,alert\n")
    for r in rows:
        fh.write(f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]},{r[5]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {"checks": len(rows), "alerts": alerts_count, "max_streak": max_streak},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
