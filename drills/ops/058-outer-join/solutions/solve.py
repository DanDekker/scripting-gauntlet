#!/usr/bin/env python3
"""058-outer-join — dict each side, then three sweeps over the key sets."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)


def load(name: str, fields: int) -> dict[str, tuple[str, ...]]:
    table = {}
    with (inp / name).open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        next(reader, None)
        for row in reader:
            if not any(cell.strip() for cell in row):
                continue
            cells = tuple(cell.strip() for cell in (row + [""] * fields)[:fields])
            table[cells[0].lower()] = cells[1:]
    return table


left = load("left.csv", 3)   # sku -> (name, qty)
right = load("right.csv", 2)  # sku -> (price,)

rows = []
both = left_only = right_only = 0
for sku in sorted(set(left) | set(right)):
    name, qty = left.get(sku, ("", ""))
    price = right.get(sku, ("",))[0]
    if sku in left and sku in right:
        side = "both"
        both += 1
    elif sku in left:
        side = "left"
        left_only += 1
    else:
        side = "right"
        right_only += 1
    rows.append((sku, name, qty, f"{float(price):.2f}" if price else "", side))

with (out / "joined.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["sku", "name", "qty", "price", "side"])
    writer.writerows(rows)

summary = {
    "keys": len(rows),
    "both": both,
    "left_only": left_only,
    "right_only": right_only,
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
