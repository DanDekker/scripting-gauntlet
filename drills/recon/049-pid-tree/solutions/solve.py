#!/usr/bin/env python3
"""049-pid-tree — depth by memoized recursion, descendants by BFS."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

parent: dict[int, int] = {}
command: dict[int, str] = {}
children: dict[int, list[int]] = {}
for line in (inp / "ps-snapshot.txt").read_text(encoding="utf-8").splitlines():
    fields = line.split()
    if len(fields) < 5 or not fields[0].isdigit():
        continue
    pid, ppid = int(fields[0]), int(fields[1])
    parent[pid] = ppid
    command[pid] = " ".join(fields[4:])
    children.setdefault(ppid, []).append(pid)

if not parent:
    raise SystemExit("no process rows in ps-snapshot.txt")

depth: dict[int, int] = {}


def depth_of(pid: int) -> int:
    if pid not in depth:
        ppid = parent[pid]
        depth[pid] = 0 if ppid not in parent else depth_of(ppid) + 1
    return depth[pid]


rows = [(pid, parent[pid], depth_of(pid), command[pid]) for pid in parent]
rows.sort(key=lambda row: (row[2], row[0]))

with (out / "tree.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("pid,ppid,depth,command\n")
    for pid, ppid, d, cmd in rows:
        fh.write(f"{pid},{ppid},{d},{cmd}\n")

queue = list(children.get(205, []))
descendants = []
while queue:
    pid = queue.pop(0)
    descendants.append(pid)
    queue.extend(children.get(pid, []))
(out / "descendants.txt").write_text(
    "".join(f"{pid}\n" for pid in sorted(descendants)), encoding="utf-8"
)

orphans = sorted(pid for pid in parent if parent[pid] != 0 and parent[pid] not in parent)
with (out / "orphans.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("pid,ppid,command\n")
    for pid in orphans:
        fh.write(f"{pid},{parent[pid]},{command[pid]}\n")

summary = {
    "processes": len(rows),
    "roots": sum(1 for row in rows if row[2] == 0),
    "max_depth": max(row[2] for row in rows),
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
