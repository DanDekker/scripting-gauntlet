#!/usr/bin/env python3
"""048-ps-snapshot — split each row, rejoin the command tail, sort twice."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

rows = []
for line in (inp / "ps-snapshot.txt").read_text(encoding="utf-8").splitlines():
    fields = line.split()
    if len(fields) < 5 or not fields[0].isdigit():
        continue
    rows.append(
        (int(fields[0]), int(fields[1]), int(fields[2]), float(fields[3]), " ".join(fields[4:]))
    )

if not rows:
    raise SystemExit("no process rows in ps-snapshot.txt")

with (out / "top_rss.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("pid,ppid,rss_kb,cpu,command\n")
    for pid, ppid, rss, cpu, command in sorted(rows, key=lambda r: (-r[2], r[0]))[:5]:
        fh.write(f"{pid},{ppid},{rss},{cpu:.1f},{command}\n")

counts: dict[str, int] = {}
for row in rows:
    token = row[4].split()[0]
    executable = token if token.startswith("[") else token.rsplit("/", 1)[-1]
    counts[executable] = counts.get(executable, 0) + 1

with (out / "commands.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("command,processes\n")
    for executable, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        fh.write(f"{executable},{n}\n")

summary = {
    "processes": len(rows),
    "total_rss_kb": sum(row[2] for row in rows),
    "commands": len(counts),
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
