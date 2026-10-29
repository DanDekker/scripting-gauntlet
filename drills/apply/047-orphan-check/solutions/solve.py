#!/usr/bin/env python3
"""047-orphan-check — collect parents first, then check every child row."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)


def records(name: str) -> list[list[str]]:
    with (inp / name).open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        next(reader, None)
        return [row for row in reader if any(cell.strip() for cell in row)]


customers = records("customers.csv")
orders = records("orders.csv")
items = records("items.csv")

customer_ids = {row[0].strip() for row in customers}
order_ids = {row[0].strip() for row in orders}

orphans = []
for index, row in enumerate(orders, start=1):
    key = row[1].strip()
    if key != "0" and key not in customer_ids:
        orphans.append(("orders.csv", index, "customer_id", key, "customers.csv"))
for index, row in enumerate(items, start=1):
    key = row[1].strip()
    if key not in order_ids:
        orphans.append(("items.csv", index, "order_id", key, "orders.csv"))

orphans.sort(key=lambda row: (row[0], row[1]))
with (out / "orphans.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("child_file,child_row,column,key_value,parent_file\n")
    for row in orphans:
        fh.write(",".join(str(cell) for cell in row) + "\n")

orphan_orders = sum(1 for row in orphans if row[0] == "orders.csv")
orphan_items = sum(1 for row in orphans if row[0] == "items.csv")
(out / "summary.json").write_text(
    json.dumps(
        {
            "customers": len(customers),
            "orders": len(orders),
            "items": len(items),
            "orphan_orders": orphan_orders,
            "orphan_items": orphan_items,
            "orphan_rows": orphan_orders + orphan_items,
        }
    )
    + "\n",
    encoding="utf-8",
)
