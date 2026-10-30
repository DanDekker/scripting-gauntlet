#!/usr/bin/env python3
"""229-perl-log-retention — python twin."""

import json
import os
import re
from datetime import date
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

policy = {}
for line in (IN / "policy.ini").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    k, _, v = line.partition("=")
    policy[k.strip()] = v.strip()

today = date.fromisoformat(policy["today"])
compress_days = int(policy["compress_days"])
delete_days = int(policy["delete_days"])

log_dir = IN / "logs"
files = sorted([f.name for f in log_dir.iterdir() if f.is_file()])

rows = []
counts = {"keep": 0, "compress": 0, "delete": 0, "ignore": 0}

pattern = re.compile(r"^[a-z]+-(\d{4}-\d{2}-\d{2})\.log(?:\.gz)?$")

for file_name in files:
    if file_name.endswith(".tmp"):
        age_str = ""
        action = "delete"
    else:
        m = pattern.match(file_name)
        if m:
            log_date = date.fromisoformat(m.group(1))
            age = (today - log_date).days
            age_str = str(age)
            if age >= delete_days:
                action = "delete"
            elif age >= compress_days and not file_name.endswith(".gz"):
                action = "compress"
            else:
                action = "keep"
        else:
            age_str = ""
            action = "ignore"

    counts[action] += 1
    rows.append((file_name, age_str, action))

with (OUT / "retention.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("file,age_days,action\n")
    for r in rows:
        fh.write(",".join(r) + "\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "files": len(rows),
            "keep": counts["keep"],
            "compress": counts["compress"],
            "delete": counts["delete"],
            "ignore": counts["ignore"],
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
