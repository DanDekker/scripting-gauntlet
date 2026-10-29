#!/usr/bin/env python3
"""087-schema-search - header first, rows second, sum by column name."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

dump = inp / "dump"
want = []
for raw in (inp / "hint.txt").read_text(encoding="utf-8").splitlines():
    key, _, value = raw.partition(":")
    if key.strip() == "columns":
        want = [cell.strip().lower() for cell in value.split(",") if cell.strip()]
if not want:
    raise SystemExit("hint names no columns")


def header_of(path: Path, delimiter: str):
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    lines = text.splitlines()
    if not lines:
        return None
    cells = [cell.strip().strip('"').strip().lower() for cell in lines[0].lstrip("\ufeff").split(delimiter)]
    return lines, cells


scanned = 0
matches = []
for dirpath, dirnames, filenames in os.walk(dump, followlinks=False):
    dirnames[:] = sorted(name for name in dirnames if not name.startswith("."))
    for name in sorted(filenames):
        path = Path(dirpath) / name
        suffix = path.suffix.lower()
        if suffix not in (".csv", ".tsv") or path.is_symlink():
            continue
        scanned += 1
        delimiter = "," if suffix == ".csv" else "\t"
        parsed = header_of(path, delimiter)
        if parsed is None:
            continue
        lines, header = parsed
        if not all(column in header for column in want):
            continue
        rows = sum(1 for line in lines[1:] if line.strip())
        budget = header.index("budget")
        total = 0.0
        for line in lines[1:]:
            if not line.strip():
                continue
            cells = [cell.strip().strip('"') for cell in line.split(delimiter)]
            if budget < len(cells) and cells[budget]:
                try:
                    total += float(cells[budget])
                except ValueError:
                    raise SystemExit(f"non-numeric budget in {path}")
        matches.append(
            {
                "path": str(path.relative_to(dump)),
                "delimiter": "comma" if delimiter == "," else "tab",
                "columns": len(header),
                "rows": rows,
                "total": total,
            }
        )

matches.sort(key=lambda row: row["path"])
with (out / "matches.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("path,delimiter,columns,rows\n")
    for row in matches:
        fh.write(f"{row['path']},{row['delimiter']},{row['columns']},{row['rows']}\n")

(out / "summary.json").write_text(
    json.dumps({"files_scanned": scanned, "matches": len(matches)}) + "\n", encoding="utf-8"
)
if not matches:
    raise SystemExit("no table has all the wanted columns")

winner = sorted(matches, key=lambda row: (-row["rows"], row["path"]))[0]
(out / "found.json").write_text(
    json.dumps(
        {"path": winner["path"], "rows": winner["rows"], "total": round(winner["total"], 2)}
    )
    + "\n",
    encoding="utf-8",
)
