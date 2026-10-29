#!/usr/bin/env python3
"""Build the messy tree for 076-runaway-files with known sizes."""

import os
from pathlib import Path

inp = Path(os.environ["IN"])
tree = inp / "tree"
tree.mkdir(parents=True, exist_ok=True)

CHUNK = b"x" * (1 << 20)


def write(rel: str, size: int) -> Path:
    path = tree / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fh:
        remaining = size
        while remaining:
            chunk = CHUNK[: min(len(CHUNK), remaining)]
            fh.write(chunk)
            remaining -= len(chunk)
    return path


write("var/log/app.log", 3 * 1048576)
write("var/log/app.log.1", 8 * 1048576)
write("var/log/old/app-2025.log", 1572864)

blob = write("var/cache/blob.bin", 5 * 1048576)
os.link(blob, tree / "var/cache/blob.bin.hard")

write("home/pp/backups/dump.sql", 10 * 1048576)
write("home/pp/old notes.txt", 1200)
write("deep/a/b/c/d/e/leaf.dat", 700000)

write("srv/site/node_modules/lib.js", 2 * 1048576)
write("srv/site/node_modules/.cache/bundle", 4 * 1048576)

(tree / "tmp").mkdir(parents=True, exist_ok=True)
os.symlink("../var", tree / "tmp" / "loop")
os.symlink("self", tree / "tmp" / "self")
