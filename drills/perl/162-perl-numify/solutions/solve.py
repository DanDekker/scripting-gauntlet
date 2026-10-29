#!/usr/bin/env python3
"""162-perl-numify — same contract; Decimal keeps the truncation exact."""

import json
import os
import re
from decimal import Decimal
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

NUMBER_RE = re.compile(r"^[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)$")

rows = []
counts = {"int": 0, "decimal": 0, "invalid": 0}

for raw in (IN / "values.txt").read_text(encoding="utf-8").splitlines():
    token = raw.strip()
    if not token:
        continue
    kind = "invalid"
    int_part = ""
    if NUMBER_RE.match(token):
        kind = "decimal" if "." in token else "int"
        int_part = str(int(Decimal(token)))  # truncates toward zero
    counts[kind] += 1
    rows.append((token, kind, int_part))

with (OUT / "values.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("token,kind,int_part\n")
    for row in rows:
        fh.write(",".join(row) + "\n")

(OUT / "summary.json").write_text(
    json.dumps({"rows": len(rows), **counts}) + "\n", encoding="utf-8"
)
