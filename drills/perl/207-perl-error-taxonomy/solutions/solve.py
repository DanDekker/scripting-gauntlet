#!/usr/bin/env python3
"""207-perl-error-taxonomy — python twin with subprocess, OSError and exceptions."""

import csv
import errno
import json
import os
import subprocess
import sys
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

probes = []
with (IN / "probes.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    next(reader, None)
    for record in reader:
        if record:
            probes.append(record)

rows = []
failed = 0

for record in probes:
    probe_id, kind, arg = (record + ["", "", ""])[:3]
    if kind == "exit":
        proc = subprocess.run(
            [sys.executable, "-c", "import sys; sys.exit(int(sys.argv[1]))", arg],
            capture_output=True,
        )
        detail = proc.returncode
        status = "ok" if detail == 0 else "failed"
    elif kind == "die":
        try:
            raise RuntimeError(arg)
        except RuntimeError as exc:
            detail = str(exc)
        status = "failed"
    elif kind == "open":
        try:
            with (IN / arg).open("rb") as fh:
                fh.read()
        except OSError as exc:
            detail = exc.errno if exc.errno is not None else 0
            status = "failed"
        else:
            detail = 0
            status = "ok"
    else:
        raise SystemExit(f"unknown probe kind: {kind}")

    failed += 1 if status == "failed" else 0
    rows.append((probe_id, kind, status, detail))

with (OUT / "results.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("id,kind,status,detail\n")
    for row in rows:
        fh.write(f"{row[0]},{row[1]},{row[2]},{row[3]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {"probes": len(rows), "failed": failed, "ok": len(rows) - failed},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
