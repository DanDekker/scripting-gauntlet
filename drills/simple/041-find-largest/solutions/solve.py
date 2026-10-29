#!/usr/bin/env python3
"""041-find-largest — size the leaves with os.walk, sort once."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

sizes = []
for root, _dirs, files in os.walk(inp):
    for name in files:
        path = Path(root) / name
        if path.is_file() and not path.is_symlink():
            sizes.append((path.relative_to(inp).as_posix(), path.stat().st_size))

sizes.sort(key=lambda item: (-item[1], item[0]))

with (out / "sizes.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("path,bytes\n")
    for rel, size in sizes:
        fh.write(f"{rel},{size}\n")

(out / "largest.json").write_text(
    json.dumps(
        {
            "files": len(sizes),
            "bytes": sum(size for _, size in sizes),
            "largest": sizes[0][0] if sizes else "",
        }
    )
    + "\n",
    encoding="utf-8",
)
