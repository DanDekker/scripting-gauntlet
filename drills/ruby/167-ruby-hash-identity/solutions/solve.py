#!/usr/bin/env python3
"""167-ruby-hash-identity — same contract; python's dict already separates 1 from "1"
and merges 1 with 1.0 only if you normalize, so the rule is the same."""

import json
import os
from collections import Counter
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

counts: Counter = Counter()
events = invalid = 0

for raw in (IN / "events.jsonl").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line:
        continue
    record = json.loads(line)
    value = record.get("id")
    if value is None:
        invalid += 1
        continue
    if isinstance(value, str):
        key = ("string", value)
    else:
        number = int(value) if float(value).is_integer() else value
        key = ("numeric", str(number))
    counts[key] += 1
    events += 1

rows = sorted(counts, key=lambda key: (key[1].encode(), key[0]))

with (OUT / "tally.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("id,kind,events\n")
    for kind, id_text in rows:
        fh.write(f"{id_text},{kind},{counts[(kind, id_text)]}\n")

(OUT / "summary.json").write_text(
    json.dumps({"ids": len(rows), "events": events, "invalid": invalid}) + "\n",
    encoding="utf-8",
)
