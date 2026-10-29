#!/usr/bin/env python3
"""050-listeners — LISTEN is the last field, the port is after the last dot."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

tcp_rows = 0
listeners: set[tuple[int, str]] = set()
for line in (inp / "netstat-an.txt").read_text(encoding="utf-8").splitlines():
    fields = line.split()
    if not fields or not fields[0].startswith("tcp"):
        continue
    tcp_rows += 1
    if fields[-1] != "LISTEN":
        continue
    address, _, port = fields[3].rpartition(".")
    listeners.add((int(port), address))

ordered = sorted(listeners)
wildcard_ports = {port for port, address in ordered if address == "*"}
conflicts = [(port, address) for port, address in ordered if address != "*" and port in wildcard_ports]

with (out / "listeners.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("port,address\n")
    for port, address in ordered:
        fh.write(f"{port},{address}\n")

with (out / "conflicts.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("port,address\n")
    for port, address in conflicts:
        fh.write(f"{port},{address}\n")

summary = {"tcp_rows": tcp_rows, "listeners": len(ordered), "conflicts": len(conflicts)}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
