#!/usr/bin/env python3
"""182-ruby-hash-default — same contract; collections.defaultdict(list) is Ruby's block
default, while a shared mutable default is the bug this drills."""

import json
import os
from collections import Counter, defaultdict
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

counts: Counter = Counter()
tags: dict[str, list[str]] = defaultdict(list)
events = 0

for raw in (IN / "events.txt").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    user, _, tag = line.partition(" ")
    counts[user] += 1
    tags[user].append(tag.strip())
    events += 1

users = sorted(counts)
with (OUT / "tally.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("user,count,tags\n")
    for user in users:
        fh.write(f"{user},{counts[user]},{';'.join(sorted(tags[user]))}\n")

(OUT / "summary.json").write_text(
    json.dumps({"users": len(users), "events": events}) + "\n", encoding="utf-8"
)
