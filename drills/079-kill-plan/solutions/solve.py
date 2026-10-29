#!/usr/bin/env python3
"""079-kill-plan - hot, unprotected, alive; deepest first, KILL only for memory."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

protected = set()
for raw in (inp / "protected.txt").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if line and not line.startswith("#"):
        protected.add(line)

processes = {}
for raw in (inp / "ps.txt").read_text(encoding="utf-8").splitlines():
    fields = raw.split()
    if len(fields) < 7 or fields[0] == "PID":
        continue
    pid, ppid, stat, cpu, mem, command = (
        int(fields[0]), int(fields[1]), fields[2], float(fields[3]), float(fields[4]), fields[6]
    )
    processes[pid] = {"ppid": ppid, "stat": stat, "cpu": cpu, "mem": mem, "command": command}


def depth(pid: int) -> int:
    hops = 0
    current = pid
    seen = set()
    while current in processes and current not in seen:
        seen.add(current)
        parent = processes[current]["ppid"]
        if parent == 0 or parent not in processes:
            break
        current = parent
        hops += 1
    return hops


plan = []
skipped = 0
for pid, info in processes.items():
    if info["cpu"] < 20 and info["mem"] < 20:
        continue
    if pid == 1 or info["stat"].startswith("Z") or info["command"] in protected:
        skipped += 1
        continue
    signal = "KILL" if info["mem"] >= 40 else "TERM"
    plan.append((depth(pid), info["cpu"], pid, signal, info["command"]))

plan.sort(key=lambda row: (-row[0], -row[1], row[2]))
with (out / "plan.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("pid,signal,command\n")
    for _depth, _cpu, pid, signal, command in plan:
        fh.write(f"{pid},{signal},{command}\n")

summary = {
    "candidates": len(plan),
    "kill": sum(1 for row in plan if row[3] == "KILL"),
    "term": sum(1 for row in plan if row[3] == "TERM"),
    "skipped": skipped,
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
