#!/usr/bin/env python3
"""234-perl-jsonl-filter — python twin."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

stats = {}
total_events = 0
total_errors = 0
total_duration = 0

for line in (IN / "events.jsonl").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line:
        continue
    obj = json.loads(line)
    svc = obj["service"]
    dur = int(obj["duration_ms"])
    is_err = 1 if obj.get("level") == "ERROR" else 0

    if svc not in stats:
        stats[svc] = {"events": 0, "errors": 0, "duration": 0}
    stats[svc]["events"] += 1
    stats[svc]["errors"] += is_err
    stats[svc]["duration"] += dur

    total_events += 1
    total_errors += is_err
    total_duration += dur

sorted_svcs = sorted(
    stats.keys(),
    key=lambda s: (-stats[s]["errors"], -stats[s]["events"], s),
)

with (OUT / "services.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("service,events,errors,total_duration_ms,avg_duration_ms\n")
    for s in sorted_svcs:
        e = stats[s]["events"]
        err = stats[s]["errors"]
        tot = stats[s]["duration"]
        avg = tot / e
        fh.write(f"{s},{e},{err},{tot},{avg:.1f}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "total_events": total_events,
            "total_errors": total_errors,
            "total_duration_ms": total_duration,
            "services_count": len(sorted_svcs),
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
