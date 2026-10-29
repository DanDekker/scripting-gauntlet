"""Build the directory tree for 159-lua-disk-scan.

The tree carries a symlink, a node_modules directory and a dot-directory, which is why
it is generated rather than committed.
"""

import os
from pathlib import Path

tree = Path(os.environ["IN"]) / "tree"
for sub in ("sub/deep", "node_modules", ".hidden"):
    (tree / sub).mkdir(parents=True, exist_ok=True)

FILES = {
    "a.log": 120,
    "b.LOG": 30,
    "notes.txt": 10,
    ".env": 5,
    "data": 0,
    "sub/c.log": 200,
    "sub/d.tar.gz": 40,
    "sub/deep/e.md": 7,
    "node_modules/x.log": 999,
    ".hidden/y.log": 50,
}

for name, size in FILES.items():
    (tree / name).write_bytes(b"x" * size)

link = tree / "link.log"
if not link.is_symlink():
    link.symlink_to("a.log")
