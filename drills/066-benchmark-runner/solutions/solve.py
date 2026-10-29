#!/usr/bin/env python3
"""Run child-process microbenchmarks and report robust timing summaries."""

import csv
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

root = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
config = json.loads((root / "config.json").read_text(encoding="utf-8"))
samples = []
summaries = []


def run_case(name, iterations):
    result = subprocess.run(
        [sys.executable, str(root / "workload.py"), name, str(iterations)],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise SystemExit(f"benchmark failed: {name}: {result.stderr.strip()}")
    output = result.stdout.strip()
    if not output.isdigit():
        raise SystemExit(f"invalid checksum for {name}: {output!r}")
    return output


for case in config["cases"]:
    for _ in range(config["warmups"]):
        run_case(case, config["iterations"])
    times = []
    checksum = None
    for run in range(1, config["samples"] + 1):
        start = time.perf_counter()
        output = run_case(case, config["iterations"])
        elapsed = time.perf_counter() - start
        if checksum is not None and output != checksum:
            raise SystemExit(f"checksum changed for {case}")
        checksum = output
        times.append(elapsed)
        samples.append((case, run, elapsed, checksum))
    ordered = sorted(times)
    p95 = ordered[int(0.95 * len(ordered) + 0.999999) - 1]
    summaries.append((case, len(times), statistics.median(times), p95, checksum))

with (out / "samples.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.writer(stream)
    writer.writerow(["case", "run", "seconds", "checksum"])
    for row in sorted(samples, key=lambda row: (row[0], row[1])):
        writer.writerow([row[0], row[1], f"{row[2]:.6f}", row[3]])
with (out / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.writer(stream)
    writer.writerow(["case", "samples", "median_seconds", "p95_seconds", "checksum"])
    for row in sorted(summaries):
        writer.writerow([row[0], row[1], f"{row[2]:.6f}", f"{row[3]:.6f}", row[4]])
(out / "summary.json").write_text(
    json.dumps({
        "cases": len(config["cases"]),
        "warmups_per_case": config["warmups"],
        "samples_per_case": config["samples"],
    }) + "\n",
    encoding="utf-8",
)
