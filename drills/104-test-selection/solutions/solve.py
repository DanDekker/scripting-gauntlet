#!/usr/bin/env python3
"""Pick the tests to run: the import graph decides, not the file list."""

import json
import os
from pathlib import Path

HEADER = ("module", "imports")


def module_of(path: str) -> str:
    """The module a path names: basename, last extension stripped."""
    base = path.rsplit("/", 1)[-1]
    dot = base.rfind(".")
    if dot > 0:
        base = base[:dot]
    return base


def load_graph(path: Path):
    keys: set[str] = set()
    edges: dict[str, set[str]] = {}
    for index, raw in enumerate(path.read_text(encoding="utf-8").splitlines()):
        line = raw.strip()
        if not line:
            continue
        fields = [field.strip() for field in line.split(",")]
        if index == 0 and tuple(fields[:2]) == HEADER:
            continue
        if len(fields) < 2:
            continue
        module, imports = fields[0], fields[1]
        if not module:
            continue
        keys.add(module)
        if not imports or imports == module:
            continue
        edges.setdefault(module, set()).add(imports)
    return keys, edges


def closure(root: str, keys: set[str], edges: dict[str, set[str]]) -> set[str]:
    if root not in keys:
        return set()
    seen = {root}
    stack = [root]
    while stack:
        node = stack.pop()
        for nxt in edges.get(node, ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def read_changes(path: Path) -> list[str]:
    changes: list[str] = []
    seen: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        name = raw.strip()
        if not name or name in seen:
            continue
        seen.add(name)
        changes.append(name)
    return sorted(changes)


def main() -> None:
    inp = Path(os.environ["IN"])
    out = Path(os.environ["OUT"])
    out.mkdir(parents=True, exist_ok=True)

    keys, edges = load_graph(inp / "graph.csv")
    changes = read_changes(inp / "changes.txt")

    known_paths = [path for path in changes if module_of(path) in keys]
    changed_modules = {module_of(path) for path in known_paths}

    tests = sorted(key for key in keys if key.startswith("tests/") and len(key) > len("tests/"))
    selected = [
        test
        for test in tests
        if changed_modules & closure(module_of(test), keys, edges)
    ]

    (out / "selected.txt").write_text(
        "".join(f"{test}\n" for test in selected), encoding="utf-8"
    )

    summary = {
        "changes": len(changes),
        "known": len(known_paths),
        "unknown": len(changes) - len(known_paths),
        "tests": len(tests),
        "selected": len(selected),
        "unused": len(tests) - len(selected),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
