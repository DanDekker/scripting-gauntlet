#!/usr/bin/env python3
"""226-perl-child-status — python twin.

subprocess reports the exit code directly and a signal death as a negative
returncode, so the classification is a different route to the same answer.
"""

import json
import os
import subprocess
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

rows = []
counts = {"ok": 0, "failed": 0, "signalled": 0, "notfound": 0}

for line in (IN / "probes.csv").read_text(encoding="utf-8").splitlines()[1:]:
    if not line.strip():
        continue
    probe_id, kind, arg = line.split(",")
    probe_id, kind, arg = probe_id.strip(), kind.strip(), arg.strip()

    if kind == "exit":
        proc = subprocess.run(
            ["python3", "-c", "import sys; sys.exit(int(sys.argv[1]))", arg]
        )
        code = proc.returncode
        status = "ok" if code == 0 else "failed"
        detail = code
    elif kind == "signal":
        proc = subprocess.run(
            [
                "python3",
                "-c",
                "import os, signal, sys; os.kill(os.getpid(), int(sys.argv[1]))",
                arg,
            ]
        )
        # A signalled child comes back as a negative returncode.
        status = "signalled"
        detail = -proc.returncode
    elif kind == "missing":
        try:
            proc = subprocess.run([arg])
        except FileNotFoundError:
            status, detail = "notfound", -1
        else:
            code = proc.returncode
            status = "ok" if code == 0 else "failed"
            detail = code
    else:
        raise SystemExit(f"unknown probe kind: {kind}")

    counts[status] += 1
    rows.append((probe_id, kind, status, detail))

with (OUT / "results.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("id,kind,status,detail\n")
    for row in rows:
        fh.write(",".join(str(cell) for cell in row) + "\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "probes": len(rows),
            "ok": counts["ok"],
            "failed": counts["failed"],
            "signalled": counts["signalled"],
            "notfound": counts["notfound"],
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
