#!/usr/bin/env python3
"""Repo map: the skip list and the kind rules decide what an agent ever sees."""

import json
import os
from pathlib import Path

SKIP_DIRS = {"node_modules", "__pycache__", ".git", "dist"}
CONFIG_NAMES = {"package.json", "Makefile", "pyproject.toml", "setup.cfg", "tsconfig.json"}
EXT_KINDS = {"py": "py", "js": "js", "mjs": "js", "cjs": "js", "ts": "ts", "tsx": "ts", "md": "md"}


def split_ext(base: str) -> tuple[str, str]:
    dot = base.rfind(".")
    if dot > 0:
        return base[:dot], base[dot + 1:].lower()
    return base, ""


def kind_of(base: str) -> str:
    stem, ext = split_ext(base)
    if stem.endswith(".test") or stem.endswith("_test"):
        return "test"
    if base in CONFIG_NAMES:
        return "config"
    return EXT_KINDS.get(ext, "other")


def main() -> None:
    inp = Path(os.environ["IN"])
    out = Path(os.environ["OUT"])
    out.mkdir(parents=True, exist_ok=True)

    tree = inp / "tree"
    if not tree.is_dir():
        raise SystemExit(f"missing input tree: {tree}")

    kinds: dict[str, list[int]] = {}
    dirs: dict[str, int] = {}
    skipped = 0
    total_bytes = 0
    largest = 0
    files = 0

    for dirpath, dirnames, filenames in os.walk(tree):
        dirnames[:] = sorted(name for name in dirnames if name not in SKIP_DIRS)
        here = Path(dirpath)
        for name in sorted(filenames):
            path = here / name
            if name.startswith("."):
                skipped += 1
                continue
            if not path.is_file():
                continue
            size = path.stat().st_size
            rel = path.relative_to(tree).as_posix()
            parts = rel.split("/")
            top = parts[0] if len(parts) > 1 else "(root)"

            kind = kind_of(name)
            entry = kinds.setdefault(kind, [0, 0])
            entry[0] += 1
            entry[1] += size
            dirs[top] = dirs.get(top, 0) + 1
            files += 1
            total_bytes += size
            largest = max(largest, size)

    rows = ["kind,files,bytes"]
    for kind in sorted(kinds):
        rows.append(f"{kind},{kinds[kind][0]},{kinds[kind][1]}")
    (out / "map.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

    rows = ["dir,files"]
    for name in sorted(dirs):
        rows.append(f"{name},{dirs[name]}")
    (out / "dirs.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

    summary = {
        "files": files,
        "bytes": total_bytes,
        "skipped": skipped,
        "dirs": len(dirs),
        "largest": largest,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
