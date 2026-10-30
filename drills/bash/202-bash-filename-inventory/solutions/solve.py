#!/usr/bin/env python3
"""202-bash-filename-inventory — python twin."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

tree = IN / "tree"

rows = []
for root, _dirs, names in os.walk(tree, followlinks=False):
    for name in names:
        full = Path(root) / name
        if full.is_symlink() or not full.is_file():
            continue
        relative = full.relative_to(tree).as_posix()
        rows.append((relative, full.stat().st_size))

rows.sort(key=lambda item: item[0].encode("utf-8"))

with (OUT / "manifest.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("path,bytes\n")
    for relative, size in rows:
        fh.write(f"{relative},{size}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "files": len(rows),
            "total_bytes": sum(size for _, size in rows),
            "spaces": sum(1 for relative, _ in rows if " " in relative),
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
