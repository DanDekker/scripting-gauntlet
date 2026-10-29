#!/usr/bin/env python3
"""172-lua-coroutine-pipeline — same contract with a generator; the fatal record ends
the run and the partial totals stand."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

CHUNK = 4096


def stream(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        buf = ""
        while True:
            chunk = fh.read(CHUNK)
            if not chunk:
                break
            buf += chunk
            while "\n" in buf:
                line, _, buf = buf.partition("\n")
                yield line
        if buf:
            yield buf


totals: dict[str, int] = {}
counts: dict[str, int] = {}
seen = processed = 0
aborted = None

try:
    for line in stream(IN / "stream.log"):
        seen += 1
        parts = line.split()
        if len(parts) != 3:
            raise ValueError(f"line {seen}: expected three fields")
        _user, level, amount = parts
        try:
            value = int(amount)
        except ValueError:
            raise ValueError(f"line {seen}: amount is not a number: {amount}") from None
        totals[level] = totals.get(level, 0) + value
        counts[level] = counts.get(level, 0) + 1
        processed += 1
except ValueError:
    aborted = seen

levels = sorted(totals)
with (OUT / "totals.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("level,total,count\n")
    for level in levels:
        fh.write(f"{level},{totals[level]},{counts[level]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {"lines": seen, "processed": processed, "aborted": aborted, "levels": len(levels)}
    )
    + "\n",
    encoding="utf-8",
)
