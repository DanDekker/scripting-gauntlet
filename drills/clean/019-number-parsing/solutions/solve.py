#!/usr/bin/env python3
"""019-number-parsing — strip the decoration, then let float() read the number."""

import csv
import json
import os
import re
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

NUMBER = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")


def parse(raw: str) -> float | None:
    text = raw.strip()
    negative = text.startswith("(") and text.endswith(")")
    if negative:
        text = text[1:-1].strip()
    text = re.sub(r"^[^0-9+.-]+", "", text).replace(",", "")
    text = text.removesuffix("%").strip()
    if not NUMBER.match(text):
        return None
    value = float(text)
    return -value if negative else value


rows = []
parsed = failed = 0
total = 0.0
with (inp / "amounts.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh, delimiter=";")
    next(reader, None)
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        rid, raw = (row + [""] * 2)[:2]
        value = parse(raw)
        if value is None:
            failed += 1
            rows.append((rid.strip(), ""))
        else:
            parsed += 1
            total += value
            rows.append((rid.strip(), f"{value:.2f}"))

with (out / "parsed.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["id", "value"])
    writer.writerows(rows)

summary = {"rows": len(rows), "parsed": parsed, "failed": failed, "total": round(total, 2)}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
