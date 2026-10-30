#!/usr/bin/env python3
"""244-ps1-literal-pattern — portable reference."""

import csv
import json
import os
import re
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
rows = []
matched = 0

with (inp / "services.csv").open(newline="", encoding="utf-8") as fh:
    for source in csv.DictReader(fh):
        name = source["name"].strip()
        rule = source["rule"].strip()
        is_match = re.fullmatch(re.escape(rule), name) is not None
        matched += is_match
        rows.append((name, rule, "yes" if is_match else "no"))

out.mkdir(parents=True, exist_ok=True)
with (out / "matches.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["name", "rule", "match"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps({"matched": matched, "unmatched": len(rows) - matched}, separators=(",", ":"))
    + "\n",
    encoding="utf-8",
)
