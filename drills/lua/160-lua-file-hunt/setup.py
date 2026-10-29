"""Build the search tree for 160-lua-file-hunt.

The tree carries an archive directory, a dot-directory and decoy names, so it is
generated rather than committed.
"""

import os
from pathlib import Path

tree = Path(os.environ["IN"]) / "hunt"
for sub in ("sub", "archive", ".hidden"):
    (tree / sub).mkdir(parents=True, exist_ok=True)

FILES = {
    "a.log": 140,
    "myblog": 120,
    "b.log": 90,
    "c.log.old": 150,
    "g.txt": 200,
    "sub/d.log": 100,
    "archive/e.log": 500,
    ".hidden/f.log": 500,
}

for name, size in FILES.items():
    (tree / name).write_bytes(b"y" * size)
