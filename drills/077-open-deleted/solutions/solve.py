#!/usr/bin/env python3
"""077-open-deleted - only REG, NLINK 0, and a real (deleted) suffix count."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

groups: dict[str, dict] = {}

for raw in (inp / "lsof.txt").read_text(encoding="utf-8").splitlines():
    fields = raw.split()
    if len(fields) < 10 or fields[0] == "COMMAND":
        continue
    command, pid, fd, kind, _device, size, nlink = (
        fields[0], fields[1], fields[3], fields[4], fields[5], fields[6], fields[7]
    )
    name = " ".join(fields[9:])
    if kind != "REG" or not fd[0].isdigit():
        continue
    if nlink != "0" or not name.endswith(" (deleted)") or not size.isdigit():
        continue
    entry = groups.setdefault(pid, {"command": command, "bytes": 0, "files": 0})
    entry["bytes"] += int(size)
    entry["files"] += 1

rows = sorted(groups.items(), key=lambda item: (-item[1]["bytes"], int(item[0])))
with (out / "deleted.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("pid,command,bytes_mb,files\n")
    for pid, entry in rows:
        fh.write(f"{pid},{entry['command']},{entry['bytes'] / 1048576:.2f},{entry['files']}\n")

reclaimable = sum(entry["bytes"] for entry in groups.values())
summary = {
    "processes": len(groups),
    "files": sum(entry["files"] for entry in groups.values()),
    "reclaimable_mb": round(reclaimable / 1048576, 2),
    "top_pid": int(rows[0][0]) if rows else 0,
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
