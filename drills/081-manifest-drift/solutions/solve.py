#!/usr/bin/env python3
"""081-manifest-drift - old side in a map, new side walked, then flush removals."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)


def load(name: str) -> dict[str, dict]:
    path = inp / name
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"{path}: {exc}")
    if not isinstance(data, list):
        raise SystemExit(f"{path}: expected a JSON array")
    entries = {}
    for item in data:
        if not isinstance(item, dict) or not all(
            key in item for key in ("path", "bytes", "sha256")
        ):
            raise SystemExit(f"{path}: entry missing path/bytes/sha256")
        if not isinstance(item["path"], str) or not item["path"]:
            raise SystemExit(f"{path}: entry with bad path")
        entries[item["path"]] = item
    return entries


old = load("old.json")
new = load("new.json")

rows = []
unchanged = 0
for path, item in new.items():
    if path not in old:
        rows.append((path, "added", "", item["bytes"]))
    elif old[path]["sha256"] != item["sha256"]:
        rows.append((path, "changed", old[path]["bytes"], item["bytes"]))
    else:
        unchanged += 1
for path, item in old.items():
    if path not in new:
        rows.append((path, "removed", item["bytes"], ""))

rows.sort(key=lambda row: row[0])
with (out / "drift.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("path,change,from_bytes,to_bytes\n")
    for path, change, before, after in rows:
        fh.write(f"{path},{change},{before},{after}\n")

summary = {
    "added": sum(1 for row in rows if row[1] == "added"),
    "removed": sum(1 for row in rows if row[1] == "removed"),
    "changed": sum(1 for row in rows if row[1] == "changed"),
    "unchanged": unchanged,
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
