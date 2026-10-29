#!/usr/bin/env python3
"""021-unicode-normalize — NFC, casefold, drop Mn, collapse spaces."""

import csv
import json
import os
import unicodedata
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)


def key(raw: str) -> str:
    text = unicodedata.normalize("NFC", raw).casefold()
    text = "".join(ch for ch in unicodedata.normalize("NFD", text) if not unicodedata.combining(ch))
    return " ".join(text.split())


rows = []
with (inp / "names.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    next(reader, None)
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        rid, raw = (row + [""] * 2)[:2]
        rows.append((rid.strip(), key(raw)))

with (out / "normalised.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["id", "key"])
    writer.writerows(rows)

summary = {"rows": len(rows), "distinct": len({key for _, key in rows})}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
