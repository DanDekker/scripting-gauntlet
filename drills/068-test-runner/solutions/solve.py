#!/usr/bin/env python3
"""Run a test list in child processes and preserve each result."""

import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

root = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
work = Path(os.environ["WORK"])
tests = []
for line in (root / "tests.txt").read_text(encoding="utf-8").splitlines():
    name = line.strip()
    if not name or name.startswith("#"):
        continue
    if not re.fullmatch(r"[a-z-]+", name):
        raise SystemExit(f"bad test name: {name}")
    tests.append(name)

rows = []
passed = 0
for name in tests:
    result = subprocess.run(
        [sys.executable, str(root / "test_case.py"), name],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    stdout = result.stdout.strip().replace(",", ";")
    stderr = result.stderr.strip().replace(",", ";")
    rows.append((name, result.returncode, stdout, stderr))
    if result.returncode == 0:
        passed += 1
    (work / "ran").mkdir(exist_ok=True)
    (work / "ran" / name).write_text(str(result.returncode), encoding="utf-8")

with (out / "results.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.writer(stream)
    writer.writerow(["test", "exit_code", "stdout", "stderr"])
    writer.writerows(rows)
failed = len(rows) - passed
(out / "summary.json").write_text(
    json.dumps({"tests": len(rows), "passed": passed, "failed": failed}) + "\n",
    encoding="utf-8",
)
if failed:
    raise SystemExit(f"{failed} test(s) failed")
