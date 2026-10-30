#!/usr/bin/env python3
"""255-tcl-split-fields — portable reference."""

import csv
import json
import os
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
rows = []
empty_tag = blank_name = 0
for index, raw in enumerate((inp / "records.psv").read_text(encoding="utf-8").splitlines()):
    if index == 0 or not raw.strip():
        continue
    fields = raw.split("|")
    if len(fields) != 3:
        raise ValueError(f"expected three fields: {raw}")
    record = [field.strip() for field in fields]
    record.append("empty" if record[2] == "" else "value")
    empty_tag += record[2] == ""
    blank_name += record[1] == ""
    rows.append(tuple(record))

out.mkdir(parents=True, exist_ok=True)
with (out / "records.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["id", "name", "tag", "tag_state"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps(
        {"records": len(rows), "empty_tag": empty_tag, "blank_name": blank_name},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
