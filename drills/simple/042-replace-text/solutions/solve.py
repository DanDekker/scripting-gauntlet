#!/usr/bin/env python3
"""042-replace-text — str.replace is already literal; mirror the tree."""

import json
import os
from pathlib import Path

OLD, NEW = "api.example.com", "api.internal"

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
(out / "tree").mkdir(parents=True, exist_ok=True)

scanned = replacements = 0
changed = []

for path in sorted(p for p in inp.rglob("*") if p.is_file()):
    rel = path.relative_to(inp).as_posix()
    text = path.read_text(encoding="utf-8")
    hits = text.count(OLD)
    target = out / "tree" / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.replace(OLD, NEW), encoding="utf-8")
    scanned += 1
    replacements += hits
    if hits:
        changed.append(rel)

(out / "changed.txt").write_text(
    "".join(f"{rel}\n" for rel in sorted(changed)), encoding="utf-8"
)
(out / "summary.json").write_text(
    json.dumps(
        {
            "files_scanned": scanned,
            "files_changed": len(changed),
            "replacements": replacements,
        }
    )
    + "\n",
    encoding="utf-8",
)
