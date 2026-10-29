#!/usr/bin/env python3
"""161-perl-split-limits — same contract; python's split keeps trailing empties."""

import json
import os
import re
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

SCORE_RE = re.compile(r"^[0-9]+$")

rows = []
empty_notes = empty_scores = invalid = 0

for raw in (IN / "rows.txt").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    fields = line.split(":")
    if len(fields) != 4:
        invalid += 1
        continue
    name, role, note, score = fields
    if not name or not role or (score and not SCORE_RE.match(score)):
        invalid += 1
        continue
    empty_notes += note == ""
    empty_scores += score == ""
    rows.append((name, role, note, score))

rows.sort(key=lambda row: row[0].encode())

with (OUT / "rows.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("name,role,note,score\n")
    for row in rows:
        fh.write(",".join(row) + "\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "rows": len(rows),
            "empty_notes": empty_notes,
            "empty_scores": empty_scores,
            "invalid": invalid,
        }
    )
    + "\n",
    encoding="utf-8",
)
