#!/usr/bin/env python3
"""170-ruby-float-format — same contract; Decimal does the half-away-from-zero rounding
exactly, which is what the contract asks for."""

import json
import os
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

NUMBER = re.compile(r"^-?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?$")

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

rows = []
counts = {"int": 0, "float": 0, "invalid": 0}

for raw in (IN / "amounts.txt").read_text(encoding="utf-8").splitlines():
    token = raw.strip()
    if not token:
        continue
    if NUMBER.match(token):
        if "." in token or "e" in token.lower():
            kind = "float"
            text = format(
                Decimal(token).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), "f"
            )
        else:
            kind = "int"
            text = str(int(token))
    else:
        kind, text = "invalid", ""
    counts[kind] += 1
    rows.append((token, kind, text))

with (OUT / "formatted.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("raw,kind,formatted\n")
    for row in rows:
        fh.write(",".join(row) + "\n")

(OUT / "summary.json").write_text(
    json.dumps({"lines": len(rows), **counts}) + "\n", encoding="utf-8"
)
