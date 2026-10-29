#!/usr/bin/env python3
"""005-dir-hygiene — inventory, hash, dedupe, normalize, resort, manifest."""

import hashlib
import os
import re
from pathlib import Path

inp = Path(os.environ["IN"]) / "messy"
out = Path(os.environ["OUT"])
clean_root = out / "clean"
clean_root.mkdir(parents=True, exist_ok=True)

JUNK = {".DS_Store", "Thumbs.db"}


def is_junk(name: str) -> bool:
    return name in JUNK or name.startswith("~$")


# 1-2. inventory, dropping junk and empty files
best: dict[str, tuple[str, bytes]] = {}
for path in sorted(inp.rglob("*")):
    if not path.is_file() or is_junk(path.name):
        continue
    payload = path.read_bytes()
    if not payload:
        continue
    rel = str(path.relative_to(inp)).replace(os.sep, "/")
    digest = hashlib.sha256(payload).hexdigest()
    current = best.get(digest)
    # shortest original path wins; ties by lexicographic order
    if current is None or (len(rel), rel) < (len(current[0]), current[0]):
        best[digest] = (rel, payload)


# 3-4. normalize the stem and sort into <ext>/
def split_ext(name: str) -> tuple[str, str]:
    if "." in name.lstrip("."):
        stem, _, ext = name.rpartition(".")
        return stem, ext.lower()
    return name, ""


def normalize(stem: str) -> str:
    stem = stem.lower()
    stem = re.sub(r"\s+", "-", stem)
    stem = re.sub(r"[^a-z0-9._-]", "", stem)
    return re.sub(r"-+", "-", stem)


rows = []
for digest, (rel, payload) in best.items():
    stem, ext = split_ext(rel.rsplit("/", 1)[-1])
    name = normalize(stem)
    clean = f"{ext}/{name}.{ext}" if ext else f"noext/{name}"
    rows.append((rel, clean, digest, len(payload), payload))

rows.sort(key=lambda row: row[0])

for rel, clean, digest, size, payload in rows:
    target = clean_root / clean
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)

with (out / "manifest.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("original,clean,sha256,bytes\n")
    for rel, clean, digest, size, _ in rows:
        fh.write(f"{rel},{clean},{digest},{size}\n")
