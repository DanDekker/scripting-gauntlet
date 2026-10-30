#!/usr/bin/env python3
"""232-perl-process-triage — python twin."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

thresholds = {}
for line in (IN / "thresholds.ini").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    k, _, v = line.partition("=")
    thresholds[k.strip()] = float(v.strip())

cpu_thresh = thresholds["cpu_pct"]
rss_thresh = int(thresholds["rss_kb"])

flagged = []
counts = {"cpu_only": 0, "mem_only": 0, "both": 0}
total = 0

lines = (IN / "processes.txt").read_text(encoding="utf-8").splitlines()
for line in lines[1:]:
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    total += 1
    parts = line.split(None, 10)
    user, pid_str, cpu_str, mem_str, vsz_str, rss_str, tty, stat, start, time_str, cmd = parts

    pid = int(pid_str)
    cpu = float(cpu_str)
    rss = int(rss_str)

    is_cpu = cpu >= cpu_thresh
    is_mem = rss >= rss_thresh

    if is_cpu and is_mem:
        flag = "both"
        counts["both"] += 1
    elif is_cpu:
        flag = "cpu"
        counts["cpu_only"] += 1
    elif is_mem:
        flag = "memory"
        counts["mem_only"] += 1
    else:
        continue

    flagged.append((pid, user, cpu, rss, flag, cmd))

sorted_flagged = sorted(flagged, key=lambda x: (-x[2], -x[3], x[0]))

with (OUT / "runaways.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("pid,user,cpu,rss,flag,command\n")
    for p in sorted_flagged:
        fh.write(f"{p[0]},{p[1]},{p[2]:.1f},{p[3]},{p[4]},{p[5]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "total_processes": total,
            "flagged": len(sorted_flagged),
            "cpu_only": counts["cpu_only"],
            "mem_only": counts["mem_only"],
            "both": counts["both"],
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
