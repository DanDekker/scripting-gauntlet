#!/usr/bin/env python3
"""076-runaway-files - lstat, dedupe inodes, filter components, rank."""

import json
import os
import stat
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

tree = inp / "tree"
JUNK = {"node_modules", ".cache", "__pycache__"}

seen_inodes: dict[tuple[int, int], tuple[str, int]] = {}
links_skipped = 0

for root, dirs, names in os.walk(tree, followlinks=False):
    for name in names:
        path = Path(root) / name
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode):
            continue
        rel = path.relative_to(tree).as_posix()
        inode = (info.st_dev, info.st_ino)
        if inode in seen_inodes:
            links_skipped += 1
            kept, size = seen_inodes[inode]
            if rel < kept:
                seen_inodes[inode] = (rel, size)
            continue
        seen_inodes[inode] = (rel, info.st_size)

files: list[tuple[str, int]] = []
ignored_bytes = 0
for rel, size in seen_inodes.values():
    if JUNK.intersection(Path(rel).parts):
        ignored_bytes += size
    else:
        files.append((rel, size))

files.sort(key=lambda item: (-item[1], item[0]))
with (out / "top_files.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("rank,path,size_mb\n")
    for rank, (rel, size) in enumerate(files[:5], start=1):
        fh.write(f"{rank},{rel},{size / 1048576:.2f}\n")

summary = {
    "files": len(files),
    "bytes": sum(size for _, size in files),
    "ignored_bytes": ignored_bytes,
    "links_skipped": links_skipped,
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
