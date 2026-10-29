#!/usr/bin/env python3
"""051-conn-states — one pass, two counters, two sorted reports."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

tcp_rows = connections = 0
states: dict[str, int] = {}
remotes: dict[str, int] = {}
for line in (inp / "netstat-an.txt").read_text(encoding="utf-8").splitlines():
    fields = line.split()
    if not fields or not fields[0].startswith("tcp"):
        continue
    tcp_rows += 1
    state = fields[-1]
    states[state] = states.get(state, 0) + 1
    if state != "LISTEN":
        connections += 1
    if fields[4] == "*.*":
        continue
    remote = fields[4].rpartition(".")[0]
    remotes[remote] = remotes.get(remote, 0) + 1

with (out / "states.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("state,count\n")
    for state, count in sorted(states.items(), key=lambda kv: (-kv[1], kv[0])):
        fh.write(f"{state},{count}\n")

with (out / "remote_top.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("remote,connections\n")
    for remote, count in sorted(remotes.items(), key=lambda kv: (-kv[1], kv[0]))[:3]:
        fh.write(f"{remote},{count}\n")

summary = {"tcp_rows": tcp_rows, "connections": connections, "states": len(states)}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
