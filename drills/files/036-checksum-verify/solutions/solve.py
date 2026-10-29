#!/usr/bin/env python3
"""036-checksum-verify — compare the signed manifest with the tree, then re-sign."""

import csv
import hashlib
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)
src = inp / "src"

signed = {}
for line in (inp / "manifest.sha256").read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    digest, path = line[:64], line[66:]
    signed[path.strip()] = digest.strip()

current = {}
for path in src.rglob("*"):
    if path.is_file():
        current[path.relative_to(src).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()

rows = []
for path in sorted(set(signed) | set(current)):
    expected, actual = signed.get(path, ""), current.get(path, "")
    if not actual:
        status = "MISSING"
    elif not expected:
        status = "EXTRA"
    elif expected == actual:
        status = "MATCH"
    else:
        status = "MODIFIED"
    rows.append((path, status, expected, actual))

with (out / "verify.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["path", "status", "expected", "actual"])
    writer.writerows(rows)

rebuilt = "".join(f"{digest}  {path}\n" for path, digest in sorted(current.items()))
(out / "rebuilt.sha256").write_text(rebuilt, encoding="utf-8")

counts = {status: sum(1 for row in rows if row[1] == status) for status in set(r[1] for r in rows)}
summary = {
    "manifest": len(signed),
    "match": counts.get("MATCH", 0),
    "missing": counts.get("MISSING", 0),
    "modified": counts.get("MODIFIED", 0),
    "extra": counts.get("EXTRA", 0),
}
summary["ok"] = not (summary["missing"] or summary["modified"] or summary["extra"])
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
