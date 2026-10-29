#!/usr/bin/env python3
"""199-ruby-forwardable-delegation — python twin with proxy encapsulation."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])


class SecureRegistry:

    def __init__(self):
        self._store = {}
        self.reads = 0

    def add(self, k, v):
        self._store[k] = v

    def lookup(self, k):
        self.reads += 1
        return self._store.get(k)

    def size(self):
        return len(self._store)

    def keys(self):
        return list(self._store.keys())

    # delete is intentionally not implemented


reg = SecureRegistry()
rows = []
step = 0
blocked_count = 0

for line in (IN / "actions.txt").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue

    step += 1
    parts = line.split()
    op = parts[0]
    args = parts[1:]

    if op == "add":
        reg.add(args[0], int(args[1]))
        rows.append((step, op, "ok", f"{args[0]}={args[1]}"))
    elif op == "get":
        val = reg.lookup(args[0])
        rows.append((step, op, "ok", str(val)))
    elif op == "size":
        rows.append((step, op, "ok", str(reg.size())))
    elif op == "keys":
        rows.append((step, op, "ok", ";".join(sorted(reg.keys()))))
    elif op == "delete":
        # Check attribute existence
        if hasattr(reg, "delete"):
            getattr(reg, "delete")(args[0])
            rows.append((step, op, "ok", "deleted"))
        else:
            blocked_count += 1
            rows.append((step, op, "blocked", "NoMethodError"))

with (OUT / "audit.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("step,op,status,result\n")
    for r in rows:
        fh.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "steps": len(rows),
            "reads": reg.reads,
            "blocked": blocked_count,
            "final_size": reg.size(),
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
