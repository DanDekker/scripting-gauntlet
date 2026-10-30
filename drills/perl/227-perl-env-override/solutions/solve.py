#!/usr/bin/env python3
"""227-perl-env-override — python twin.

There is no lexical local for the environment, so the twin saves the previous state,
sets the override, runs the child, and restores by hand.
"""

import csv
import json
import os
import subprocess
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

CHILD = 'print exists $ENV{$ARGV[0]} ? "=$ENV{$ARGV[0]}" : "unset"'

rows = []
seen_set = 0
leaked = 0

with (IN / "steps.csv").open(newline="", encoding="utf-8") as fh:
    records = [row for row in csv.reader(fh) if row and any(c.strip() for c in row)]

# The contract says these names start out absent; make that true even if the
# environment we inherited already had them.
for record in records[1:]:
    os.environ.pop(record[1].strip(), None)

for record in records[1:]:
    step_id, set_var, value, watch_var = (cell.strip() for cell in record)

    had = set_var in os.environ
    old = os.environ.get(set_var)
    os.environ[set_var] = value
    try:
        proc = subprocess.run(
            ["perl", "-e", CHILD, watch_var],
            capture_output=True,
            text=True,
            env=dict(os.environ),
        )
        seen = proc.stdout.strip()
    finally:
        if had:
            os.environ[set_var] = old
        else:
            os.environ.pop(set_var, None)

    after = f"={os.environ[set_var]}" if set_var in os.environ else "unset"
    if seen != "unset":
        seen_set += 1
    if after != "unset":
        leaked += 1

    rows.append((step_id, set_var, value, watch_var, seen, after))

with (OUT / "steps.csv").open("w", encoding="utf-8", newline="") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["id", "set_var", "value", "watch_var", "seen", "after"])
    for row in rows:
        writer.writerow(row)

(OUT / "summary.json").write_text(
    json.dumps(
        {"steps": len(rows), "seen_set": seen_set, "leaked": leaked},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
