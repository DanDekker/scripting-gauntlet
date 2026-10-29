#!/usr/bin/env python3
"""029-set-ops — two sets, four answers, sorted on the way out."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)


def load(path: Path) -> set[str]:
    ids = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        token = line.strip().lower()
        if token:
            ids.add(token)
    return ids


a = load(inp / "a.txt")
b = load(inp / "b.txt")

answers = {
    "union.txt": a | b,
    "both.txt": a & b,
    "only_a.txt": a - b,
    "only_b.txt": b - a,
}
for name, values in answers.items():
    (out / name).write_text("".join(f"{value}\n" for value in sorted(values)), encoding="utf-8")

summary = {
    "a": len(a),
    "b": len(b),
    "union": len(answers["union.txt"]),
    "both": len(answers["both.txt"]),
    "only_a": len(answers["only_a.txt"]),
    "only_b": len(answers["only_b.txt"]),
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
