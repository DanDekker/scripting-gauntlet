#!/usr/bin/env python3
"""078-cleanup-budget - risk first, size second, stop at the target."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

target = int((inp / "target.txt").read_text().strip())
candidates = []
for raw in (inp / "candidates.csv").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    parts = line.split(",")
    if len(parts) != 3 or not parts[1].strip().isdigit() or not parts[2].strip().isdigit():
        continue
    path, size, risk = parts[0].strip(), int(parts[1]), int(parts[2])
    if not 1 <= risk <= 5:
        raise SystemExit(f"bad risk for {path}: {risk}")
    candidates.append((risk, -size, path, size))

candidates.sort()
freed = 0
plain = []
for risk, _negated, path, size in candidates:
    if freed >= target:
        break
    freed += size
    plain.append((path, size, risk))

with (out / "cleanup.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("order,path,size_mb,risk\n")
    for order, (path, size, risk) in enumerate(plain, start=1):
        fh.write(f"{order},{path},{size},{risk}\n")

summary = {
    "target_mb": target,
    "freed_mb": freed,
    "taken": len(plain),
    "complete": freed >= target,
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
