#!/usr/bin/env python3
"""035-split-merge — split into fixed-size chunks, then prove the roundtrip."""

import json
import os
from pathlib import Path

CHUNK = 5

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

raw = (inp / "events.csv").read_bytes()
lines = raw.splitlines(keepends=True)
if len(lines) < 2:
    raise SystemExit("events.csv has no data rows")

header, body = lines[0], lines[1:]
chunks = [body[i : i + CHUNK] for i in range(0, len(body), CHUNK)]

for index, chunk in enumerate(chunks, start=1):
    (out / f"chunk_{index:02d}.csv").write_bytes(header + b"".join(chunk))

merged = header + b"".join(b"".join(chunk) for chunk in chunks)
(out / "merged.csv").write_bytes(merged)
if merged != raw:
    raise SystemExit("reassembly does not match events.csv")

report = {
    "rows": len(body),
    "chunk_size": CHUNK,
    "chunks": len(chunks),
    "roundtrip": True,
}
(out / "report.json").write_text(json.dumps(report) + "\n", encoding="utf-8")
