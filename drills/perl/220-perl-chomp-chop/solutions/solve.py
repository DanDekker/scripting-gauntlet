#!/usr/bin/env python3
"""220-perl-chomp-chop — python twin."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

# splitlines() drops the terminators and keeps the last record intact.
notes = (IN / "notes.txt").read_text(encoding="utf-8").splitlines()

chars = 0
with (OUT / "notes.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("index,text,length\n")
    for index, note in enumerate(notes, start=1):
        length = len(note)
        chars += length
        fh.write(f"{index},{note},{length}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "notes": len(notes),
            "chars": chars,
            "last": notes[-1] if notes else "",
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
