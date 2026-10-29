#!/usr/bin/env python3
"""152-lua-utf8-chars — same contract, bytes in and characters out."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])


def csv_field(value: str) -> str:
    if any(ch in value for ch in ',"\r\n'):
        return '"' + value.replace('"', '""') + '"'
    return value


raw = (IN / "mixed.txt").read_bytes()
pieces = raw.split(b"\n")
if pieces and pieces[-1] == b"":
    pieces.pop()

valid = invalid = total_chars = total_bytes = 0

with (OUT / "chars.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("line,chars,bytes,head\n")
    for index, blob in enumerate(pieces, start=1):
        if not blob:
            continue
        try:
            text = blob.decode("utf-8")
        except UnicodeDecodeError:
            invalid += 1
            continue
        valid += 1
        chars = len(text)
        bytes_count = len(blob)
        total_chars += chars
        total_bytes += bytes_count
        head = text[:10]
        fh.write(f"{index},{chars},{bytes_count},{csv_field(head)}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "lines": len(pieces),
            "valid": valid,
            "invalid": invalid,
            "chars": total_chars,
            "bytes": total_bytes,
        }
    )
    + "\n",
    encoding="utf-8",
)
