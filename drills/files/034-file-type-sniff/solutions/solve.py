#!/usr/bin/env python3
"""034-file-type-sniff — trust the magic bytes, not the name."""

import json
import os
from pathlib import Path

SIGNATURES = [
    (b"\x1f\x8b", "gzip"),
    (b"\x89PNG", "png"),
    (b"%PDF", "pdf"),
    (b"PK\x03\x04", "zip"),
    (b"\x7fELF", "elf"),
    (b"\xff\xd8\xff", "jpeg"),
    (b"\xff\xfe", "utf16le"),
    (b"\xef\xbb\xbf", "utf8bom"),
]
TEXT = {"ascii", "utf8bom", "utf16le"}

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

rows = []
for path in sorted(p for p in inp.iterdir() if p.is_file()):
    data = path.read_bytes()
    kind = next((name for sig, name in SIGNATURES if data.startswith(sig)), None)
    if kind is None:
        textish = all(0x20 <= b <= 0x7E or b in (0x09, 0x0A, 0x0D) for b in data)
        kind = "ascii" if textish else "unknown"
    rows.append((path.name, kind, data[:8].hex()))

with (out / "types.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("filename,kind,magic\n")
    for row in rows:
        fh.write(",".join(row) + "\n")

summary = {
    "files": len(rows),
    "kinds": len({kind for _, kind, _ in rows}),
    "text_files": sum(kind in TEXT for _, kind, _ in rows),
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
