#!/usr/bin/env python3
"""011-xml-attrs — xml.etree, attributes and children kept apart."""

import csv
import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

root = ET.parse(inp / "catalog.xml").getroot()

rows = []
for product in root.findall("product"):
    rows.append(
        [
            product.get("id", ""),
            product.findtext("name", ""),
            product.get("price", ""),
            "|".join((tag.text or "").strip() for tag in product.findall("tag")),
        ]
    )

rows.sort(key=lambda row: row[0])

with (out / "products.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["id", "name", "price", "tags"])
    writer.writerows(rows)

(out / "summary.json").write_text(
    json.dumps({"products": len(rows)}) + "\n", encoding="utf-8"
)
