#!/usr/bin/env python3
"""261-tcl-dict-sort — portable reference."""

import csv
import json
import os
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
counts = {}
with (inp / "counts.tsv").open(encoding="utf-8") as fh:
    next(fh)
    for raw in fh:
        if not raw.strip():
            continue
        key, amount = raw.rstrip("\n").split("\t")
        counts[key.strip()] = counts.get(key.strip(), 0) + int(amount.strip())
rows = sorted(counts.items(), key=lambda item: (-item[1], item[0]))

out.mkdir(parents=True, exist_ok=True)
with (out / "counts.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["key", "count"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps({"keys": len(rows), "total": sum(count for _, count in rows)}, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
