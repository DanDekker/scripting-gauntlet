#!/usr/bin/env python3
"""193-perl-regex-lookaround — python twin with regex lookaround."""

import json
import os
import re
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

records = []
curr_count = 0
motif_count = 0

CURR_RE = re.compile(r"(?<!\w)(USD|EUR|GBP)(\d+)(?=[,\s\.]|$)")

for line in (IN / "stream.txt").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue

    if line.startswith("AUDIT"):
        line_id, _, rest = line.partition(":")
        for m in CURR_RE.finditer(rest):
            records.append((line_id.strip(), "currency", m.group(1), int(m.group(2))))
            curr_count += 1
    elif line.startswith("MOTIF"):
        line_id, _, rest = line.partition(":")
        m = re.search(r"target=(\S+)\s+seq=(\S+)", rest)
        if m:
            target, seq = m.group(1), m.group(2)
            pattern = re.compile(rf"(?=({re.escape(target)}))")
            for match in pattern.finditer(seq):
                motif = match.group(1)
                offset = match.start() + 1
                records.append((line_id.strip(), "motif", motif, offset))
                motif_count += 1

with (OUT / "extractions.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("id,type,key,val\n")
    for r in records:
        fh.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {"records": len(records), "currencies": curr_count, "motifs": motif_count},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
