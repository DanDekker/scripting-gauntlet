#!/usr/bin/env python3
"""088-content-hint - normalise the query once, every line once, then substring."""

import json
import os
import re
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

EXTENSIONS = {".md", ".txt", ".log"}
MAX_BYTES = 1024 * 1024


def normalise(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text.lower()).strip()


query = normalise((inp / "query.txt").read_text(encoding="utf-8"))
if not query:
    raise SystemExit("query.txt is empty")

notes = inp / "notes"
files_scanned = 0
skipped_large = 0
matching_lines = 0
matching_files = 0
rows = []

for dirpath, dirnames, filenames in os.walk(notes, followlinks=False):
    dirnames[:] = sorted(name for name in dirnames if not name.startswith("."))
    for name in sorted(filenames):
        path = Path(dirpath) / name
        if path.suffix.lower() not in EXTENSIONS or path.is_symlink():
            continue
        files_scanned += 1
        if path.stat().st_size > MAX_BYTES:
            skipped_large += 1
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        hits = 0
        for lineno, line in enumerate(text.splitlines(), 1):
            if query in normalise(line):
                hits += 1
                rows.append((str(path.relative_to(notes)), lineno, line.strip()))
        matching_lines += hits
        if hits:
            matching_files += 1

rows.sort(key=lambda row: (row[0], row[1]))
with (out / "matches.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("path,line,text\n")
    for relative, lineno, text in rows:
        fh.write(f"{relative},{lineno},{text}\n")

if rows:
    relative, lineno, text = rows[0]
    (out / "match.json").write_text(
        json.dumps({"path": relative, "line": lineno, "text": text}) + "\n",
        encoding="utf-8",
    )

(out / "summary.json").write_text(
    json.dumps(
        {
            "files_scanned": files_scanned,
            "matching_files": matching_files,
            "matching_lines": matching_lines,
            "skipped_large": skipped_large,
        }
    )
    + "\n",
    encoding="utf-8",
)
