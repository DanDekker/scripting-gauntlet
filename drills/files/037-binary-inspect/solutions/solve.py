#!/usr/bin/env python3
"""037-binary-inspect — walk the blob byte by byte."""

import json
import os
from pathlib import Path

SIGNATURES = [
    (b"\x89PNG", "png"),
    (b"\x1f\x8b", "gzip"),
    (b"%PDF", "pdf"),
    (b"PK\x03\x04", "zip"),
    (b"\x7fELF", "elf"),
    (b"\xff\xd8\xff", "jpeg"),
]

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

data = (inp / "blob.bin").read_bytes()

strings = []
start = None
for offset, byte in enumerate(data):
    if 0x20 <= byte <= 0x7E:
        if start is None:
            start = offset
    elif start is not None:
        if offset - start >= 4:
            strings.append((start, data[start:offset].decode("ascii")))
        start = None
if start is not None and len(data) - start >= 4:
    strings.append((start, data[start:].decode("ascii")))

magic, magic_offset = "none", -1
for offset in range(len(data)):
    hit = next((name for sig, name in SIGNATURES if data.startswith(sig, offset)), None)
    if hit:
        magic, magic_offset = hit, offset
        break

with (out / "strings.txt").open("w", encoding="utf-8", newline="") as fh:
    for offset, text in strings:
        fh.write(f"{offset}\t{text}\n")

report = {
    "size_bytes": len(data),
    "nul_bytes": data.count(0),
    "string_count": len(strings),
    "embedded_magic": magic,
    "magic_offset": magic_offset,
}
(out / "report.json").write_text(json.dumps(report) + "\n", encoding="utf-8")
