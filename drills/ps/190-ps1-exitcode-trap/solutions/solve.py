#!/usr/bin/env python3
"""190-ps1-exitcode-trap — python twin with subprocess execution."""

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

steps = []
with (IN / "steps.csv").open(newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        steps.append(row)

results = []
succeeded = 0
failed = 0

for step in steps:
    target_code = int(step["code"])
    proc = subprocess.run(
        [sys.executable, "-c", "import sys; sys.exit(int(sys.argv[1]))", str(target_code)],
        capture_output=True,
    )
    actual_code = proc.returncode
    if actual_code == 0:
        succeeded += 1
        status = "success"
    else:
        failed += 1
        status = "failed"
    results.append((int(step["id"]), step["action"], actual_code, status))

with (OUT / "results.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("id,action,code,status\n")
    for r in results:
        fh.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {"total_steps": len(results), "succeeded": succeeded, "failed": failed},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
