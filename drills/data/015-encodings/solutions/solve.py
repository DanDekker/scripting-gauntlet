#!/usr/bin/env python3
"""015-encodings — decode by sniffing the first bytes, fall back when UTF-8 fails."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)


def decode(raw: bytes) -> str:
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw[3:].decode("utf-8")
    if raw.startswith(b"\xff\xfe"):
        return raw[2:].decode("utf-16-le")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


rows = []
files = 0
for path in sorted(inp.glob("*.csv")):
    files += 1
    source = path.stem
    text = decode(path.read_bytes()).replace("\r\n", "\n").replace("\r", "\n")
    for row in list(csv.reader(text.splitlines()))[1:]:
        if not row:
            continue
        rows.append((int(row[0]), source, row[1], row[2]))

rows.sort(key=lambda row: row[0])

with (out / "merged.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["id", "source", "name", "city"])
    writer.writerows(rows)

(out / "summary.json").write_text(
    json.dumps({"files": files, "rows": len(rows)}) + "\n", encoding="utf-8"
)
