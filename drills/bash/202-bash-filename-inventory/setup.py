#!/usr/bin/env python3
"""Build the messy tree for 202-bash-filename-inventory.

The names contain spaces, and there is a symlink and an empty directory.
Git cannot carry a symlink or an empty directory usefully, so they are made here.
"""

import os
from pathlib import Path

IN = Path(os.environ["IN"])
tree = IN / "tree"

files = {
    "plain.txt": b"plain\n",
    "reports/My Report.txt": b"my report\n",
    "reports/annual summary.pdf": b"%PDF-1.4 annual\n",
    "reports/notes.txt": b"notes\n",
    "weird name/deep file.dat": b"deep\n",
}

for relative, payload in files.items():
    path = tree / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)

(tree / "empty").mkdir(parents=True, exist_ok=True)

os.symlink("plain.txt", tree / "reports" / "link-to-plain")
