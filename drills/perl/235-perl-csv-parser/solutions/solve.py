#!/usr/bin/env python3
"""235-perl-csv-parser — python twin."""

import csv
import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

valid_rows = []
total_rows = 0
malformed = 0
total_amount = 0.0

with (IN / "orders.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    header = next(reader, None)
    for row in reader:
        if not row:
            continue
        total_rows += 1
        if len(row) != 5:
            malformed += 1
            continue
        valid_rows.append(row)
        total_amount += float(row[3])

with (OUT / "clean.tsv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("order_id\tcustomer\tproduct\tamount\tnotes\n")
    for r in valid_rows:
        fh.write("\t".join(r) + "\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "total_rows": total_rows,
            "valid": len(valid_rows),
            "malformed": malformed,
            "total_amount": round(total_amount, 2),
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
