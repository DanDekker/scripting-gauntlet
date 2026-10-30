#!/usr/bin/env python3
"""256-tcl-dict-presence — portable reference."""

import csv
import json
import os
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
settings = {}
for raw in (inp / "settings.tsv").read_text(encoding="utf-8").splitlines():
    if not raw:
        continue
    key, value = raw.split("\t")
    settings[key.strip()] = value.strip()

rows = []
missing = empty = zero = 0
for key in ("limit", "owner", "enabled", "region"):
    if key not in settings:
        state, value = "missing", ""
        missing += 1
    else:
        value = settings[key]
        if value == "":
            state = "empty"
            empty += 1
        elif value == "0":
            state = "zero"
            zero += 1
        else:
            state = "value"
    rows.append((key, state, value))

out.mkdir(parents=True, exist_ok=True)
with (out / "settings.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["key", "state", "value"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps(
        {"keys": len(rows), "missing": missing, "empty": empty, "zero": zero},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
