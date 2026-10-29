#!/usr/bin/env python3
"""052-resource-usage — longest-prefix mount match, then one JSON object."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

PATH = "/var/lib/app/queue.db"

mounts = []
lines = (inp / "df-k.txt").read_text(encoding="utf-8").splitlines()
for line in lines[1:]:
    fields = line.split()
    if len(fields) < 6:
        continue
    mounts.append(
        {
            "mount": " ".join(fields[5:]),
            "pct": int(fields[4].rstrip("%")),
            "available": int(fields[3]),
        }
    )

matching = [m for m in mounts if PATH == m["mount"] or PATH.startswith(m["mount"] + "/")]
if not matching:
    raise SystemExit(f"no filesystem contains {PATH}")
best = max(matching, key=lambda m: len(m["mount"]))

uptime = (inp / "uptime.txt").read_text(encoding="utf-8")
load1 = float(uptime.split("load averages:", 1)[1].split()[0].rstrip(","))
cpus = int((inp / "cpucount.txt").read_text(encoding="utf-8").split()[0])

resources = {
    "path": PATH,
    "mount": best["mount"],
    "used_pct": best["pct"],
    "available_kb": best["available"],
    "load1": load1,
    "cpus": cpus,
    "load_per_cpu": round(load1 / cpus, 2),
    "warning": best["pct"] >= 90,
    "mounts": len(mounts),
}
(out / "resources.json").write_text(json.dumps(resources) + "\n", encoding="utf-8")
