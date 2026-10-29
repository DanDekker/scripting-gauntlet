#!/usr/bin/env python3
"""010-json-flatten — walk the document, one flat row per product."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

document = json.loads((inp / "catalog.json").read_text(encoding="utf-8"))

rows = []
for product in document["products"]:
    specs = product.get("specs", {})
    rows.append(
        [
            product["sku"],
            product["name"],
            product["price"],
            specs.get("material", ""),
            specs.get("weight", ""),
            "|".join(product.get("tags", [])),
        ]
    )

rows.sort(key=lambda row: row[0])

with (out / "flat.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["sku", "name", "price", "material", "weight", "tags"])
    writer.writerows(rows)

meta = {"generated": document.get("generated"), "count": len(rows)}
(out / "meta.json").write_text(json.dumps(meta) + "\n", encoding="utf-8")
