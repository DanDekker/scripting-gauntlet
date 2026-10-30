#!/usr/bin/env python3
"""201-bash-log-rotate — python twin using datetime.date."""

import gzip
import json
import os
import re
import shutil
from datetime import date
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

policy = {}
for line in (IN / "policy.txt").read_text(encoding="utf-8").splitlines():
    if "=" in line:
        key, _, value = line.partition("=")
        policy[key.strip()] = value.strip()

today = date.fromisoformat(policy["today"])
compress_after = int(policy["compress_after_days"])
delete_after = int(policy["delete_after_days"])

pattern = re.compile(r"^svc-(\d{4})-(\d{2})-(\d{2})\.log$")

out_logs = OUT / "logs"
out_logs.mkdir(parents=True, exist_ok=True)

rows = []
kept = compressed = deleted = ignored = 0

for src in sorted((IN / "logs").iterdir()):
    if not src.is_file():
        continue
    match = pattern.match(src.name)
    if not match:
        ignored += 1
        continue
    log_date = date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    age = (today - log_date).days
    if age >= delete_after:
        action = "delete"
        deleted += 1
    elif age >= compress_after:
        action = "compress"
        compressed += 1
    else:
        action = "keep"
        kept += 1
        shutil.copyfile(src, out_logs / src.name)
    if action == "compress":
        with (out_logs / f"{src.name}.gz").open("wb") as fh:
            fh.write(gzip.compress(src.read_bytes()))
    rows.append((src.name, age, action))

with (OUT / "rotation.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("file,age_days,action\n")
    for name, age, action in sorted(rows):
        fh.write(f"{name},{age},{action}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {"kept": kept, "compressed": compressed, "deleted": deleted, "ignored": ignored},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
