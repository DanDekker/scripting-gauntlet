#!/usr/bin/env python3
"""007-quoted-fields — csv module does the parsing; three lines of real work."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

with (inp / "notes.csv").open(newline="", encoding="utf-8") as fh:
    rows = list(csv.reader(fh))

header, data = rows[0], rows[1:]
multiline = sum(1 for row in data for cell in row if "\n" in cell)

with (out / "clean.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(data)

stats = {"rows": len(data), "multiline": multiline}
(out / "stats.json").write_text(json.dumps(stats) + "\n", encoding="utf-8")
