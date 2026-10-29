#!/usr/bin/env python3
"""174-perl-unpack-binary — struct.unpack with an explicit big-endian template."""

import json
import os
import struct
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

data = (IN / "records.bin").read_bytes()
total = len(data)
if total < 4 or data[:4] != b"SRV1":
    raise SystemExit("records.bin: bad magic (expected SRV1)")

offset = 4
rows = []
truncated = 0

while offset < total:
    remaining = total - offset
    if remaining < 8:
        truncated += 1
        break
    rid, score, flags, name_len = struct.unpack(">IHBB", data[offset : offset + 8])
    if remaining < 8 + name_len:
        truncated += 1
        break
    name = data[offset + 8 : offset + 8 + name_len].decode("utf-8")
    offset += 8 + name_len
    rows.append((rid, score, flags, name))

rows.sort(key=lambda row: row[0])

with (OUT / "records.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("id,score,flags,name\n")
    for row in rows:
        fh.write(",".join(str(cell) for cell in row) + "\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {"records": len(rows), "truncated": truncated, "bytes_read": offset, "bytes_total": total}
    )
    + "\n",
    encoding="utf-8",
)
