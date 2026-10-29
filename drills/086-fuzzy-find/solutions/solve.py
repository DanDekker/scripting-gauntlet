#!/usr/bin/env python3
"""086-fuzzy-find - score by hint, break ties by mtime, then read the winner."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

tree = inp / "tree"
home = tree / "home" / "pp"

hint = {}
for raw in (inp / "hint.txt").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    key, _, value = line.partition(":")
    hint[key.strip()] = value.strip()

keywords = [word.strip().lower() for word in hint["keywords"].split(",") if word.strip()]
extension = hint["extension"].lower()
max_size = int(hint["max_size"])
roots = hint["roots"].split()

scanned = 0
candidates = []
for root in roots:
    start = home / root
    if not start.is_dir():
        raise SystemExit(f"missing root: {start}")
    for dirpath, dirnames, filenames in os.walk(start, followlinks=False):
        dirnames[:] = sorted(name for name in dirnames if not name.startswith("."))
        for name in filenames:
            path = Path(dirpath) / name
            if path.is_symlink() or not path.is_file():
                continue
            scanned += 1
            if path.suffix.lower().lstrip(".") != extension:
                continue
            if path.stat().st_size > max_size:
                continue
            score = sum(1 for word in keywords if word in name.lower())
            if score < 2:
                continue
            candidates.append(
                (score, path.stat().st_mtime, str(path.relative_to(tree)), path)
            )

candidates.sort(key=lambda row: (-row[0], -row[1], row[2]))
with (out / "candidates.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("path,score\n")
    for score, _mtime, relative, _path in candidates:
        fh.write(f"{relative},{score}\n")

if not candidates:
    raise SystemExit("no candidates matched the hint")

score, _mtime, relative, winner = candidates[0]
rows = 0
total = 0.0
with winner.open(newline="", encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    if not reader.fieldnames or [f.strip() for f in reader.fieldnames] != ["month", "amount"]:
        raise SystemExit(f"unexpected header in {relative}")
    for record in reader:
        if not (record.get("month") or "").strip():
            continue
        rows += 1
        total += float(record["amount"])

(out / "found.json").write_text(
    json.dumps({"path": relative, "score": score, "rows": rows, "total": round(total, 2)})
    + "\n",
    encoding="utf-8",
)
(out / "summary.json").write_text(
    json.dumps({"scanned": scanned, "candidates": len(candidates)}) + "\n",
    encoding="utf-8",
)
