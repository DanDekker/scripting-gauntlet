#!/usr/bin/env python3
"""195-ps1-pipeline-unrolling — python twin with list encapsulation."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

rows = []
total_items = 0
single_batches = 0
empty_batches = 0

for line in (IN / "batches.txt").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue

    id_str, _, raw = line.partition(":")
    bid = int(id_str.strip())
    raw = raw.strip()
    if not raw:
        items = []
    else:
        items = [x.strip() for x in raw.split(",") if x.strip()]

    is_arr = "true"  # Python lists never unroll implicitly
    count = len(items)
    first = items[0] if count > 0 else ""

    total_items += count
    if count == 1:
        single_batches += 1
    elif count == 0:
        empty_batches += 1

    rows.append((bid, count, is_arr, first))

with (OUT / "batches.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("id,count,is_array,first\n")
    for r in rows:
        fh.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "batches": len(rows),
            "total_items": total_items,
            "single_item_batches": single_batches,
            "empty_batches": empty_batches,
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
