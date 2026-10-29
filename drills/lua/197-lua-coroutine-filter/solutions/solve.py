#!/usr/bin/env python3
"""197-lua-coroutine-filter — python twin with generator coroutines."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])


def make_meter(threshold):
    first_delta = yield
    total = first_delta
    while True:
        delta = yield (total >= threshold, total)
        if delta is None:
            break
        total += delta


meters = {}
streams = set()
rows = []
alerts_count = 0
step = 0
final_max = 0

for line in (IN / "events.txt").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    step += 1
    stream, _, delta_str = line.partition(" ")
    delta = int(delta_str.strip())
    streams.add(stream)

    if stream not in meters:
        gen = make_meter(50)
        next(gen)  # prime generator
        meters[stream] = gen

    alert, total = meters[stream].send(delta)
    if alert:
        alerts_count += 1
    if total > final_max:
        final_max = total

    rows.append((step, stream, delta, total, "true" if alert else "false"))

with (OUT / "meter.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("step,stream,delta,sum,alert\n")
    for r in rows:
        fh.write(f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "events": len(rows),
            "streams": len(streams),
            "alerts": alerts_count,
            "final_max": final_max,
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
