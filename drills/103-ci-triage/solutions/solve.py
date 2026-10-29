#!/usr/bin/env python3
"""Triage a CI log: strip colour, take result lines, last verdict wins except ERROR."""

import csv
import json
import os
import re
from pathlib import Path

ANSI = re.compile(r"\x1b\[[0-9;]*m")
MARKER = "=== short test summary info ==="
VERDICTS = {"PASSED": "pass", "FAILED": "fail", "ERROR": "error", "SKIP": "skip"}


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    log = in_dir / "ci.log"
    if not log.is_file():
        raise SystemExit(f"{log}: no such file")

    last = {}
    sticky = set()
    in_summary = False

    for raw in log.read_text(encoding="utf-8", errors="replace").splitlines():
        line = ANSI.sub("", raw).strip()
        if line == MARKER:
            in_summary = True
            continue
        parts = line.split()
        if len(parts) < 2 or parts[0] not in VERDICTS:
            continue
        status, test = parts[0], parts[1]
        if in_summary and status != "FAILED":
            continue
        last[test] = VERDICTS[status]
        if status == "ERROR":
            sticky.add(test)

    rows = [(test, "error" if test in sticky else verdict) for test, verdict in last.items()]
    rows.sort(key=lambda row: row[0])

    with (out_dir / "results.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["test", "verdict"])
        writer.writerows(rows)

    summary = {
        "tests": len(rows),
        "passed": sum(1 for _, verdict in rows if verdict == "pass"),
        "failed": sum(1 for _, verdict in rows if verdict == "fail"),
        "errored": sum(1 for _, verdict in rows if verdict == "error"),
        "skipped": sum(1 for _, verdict in rows if verdict == "skip"),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
