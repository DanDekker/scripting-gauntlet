#!/usr/bin/env python3
"""Add the two skipped paths git refuses to store: a nested .git and a .pyc."""

import os
from pathlib import Path

tree = Path(os.environ["IN"]) / "tree"

pycache = tree / "__pycache__"
pycache.mkdir(parents=True, exist_ok=True)
(pycache / "main.cpython-311.pyc").write_bytes(b"\x00" * 64 + b"fake bytecode\n")

gitdir = tree / ".git"
gitdir.mkdir(parents=True, exist_ok=True)
(gitdir / "config").write_text("[core]\n\trepositoryformatversion = 0\n", encoding="utf-8")
