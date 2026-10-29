#!/usr/bin/env python3
"""056-network-events — split the fields once, then count."""

import json
import os
import re
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

PAIR = re.compile(r"(\w+)=(\S+)")

actions: dict[str, int] = {}
attempts: dict[str, int] = {}
events = allowed = blocked = skipped = 0

for line in (inp / "events.log").read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    fields = dict(PAIR.findall(line))
    action = fields.get("ACTION", "").upper()
    dpt = fields.get("DPT", "")
    source = fields.get("SRC", "")
    if not action or not dpt or not source:
        skipped += 1
        continue

    events += 1
    if action == "ALLOW":
        allowed += 1
    elif action in ("DROP", "REJECT"):
        blocked += 1
    actions[action] = actions.get(action, 0) + 1
    attempts[source] = attempts.get(source, 0) + 1

with (out / "actions.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("action,count\n")
    for action, count in sorted(actions.items(), key=lambda kv: (-kv[1], kv[0])):
        fh.write(f"{action},{count}\n")

with (out / "top_sources.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("source,attempts\n")
    for source, count in sorted(attempts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]:
        fh.write(f"{source},{count}\n")

summary = {"events": events, "allowed": allowed, "blocked": blocked, "skipped": skipped}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
