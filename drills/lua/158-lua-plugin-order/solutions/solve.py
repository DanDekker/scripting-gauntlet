#!/usr/bin/env python3
"""158-lua-plugin-order — same contract, dicts and fixpoints."""

import json
import os
import re
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

NAME_RE = re.compile(r"^[a-z0-9-]+$")

defined: dict[str, list[str]] = {}
names: list[str] = []
errors: dict[str, str] = {}

for raw in (IN / "plugins.txt").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    name, _, rest = line.partition(":")
    name = name.strip()
    if name in defined:
        errors.setdefault(name, "duplicate-name")
    elif not NAME_RE.match(name):
        errors.setdefault(name, "bad-name")
    else:
        defined[name] = [dep.strip() for dep in rest.split(",") if dep.strip()]
        names.append(name)

for name in names:
    for dep in defined[name]:
        if not NAME_RE.match(dep):
            errors.setdefault(name, f"bad-dep:{dep}")
        elif dep not in defined:
            errors.setdefault(name, f"missing-dep:{dep}")

# reachability: a plugin that reaches itself is in a cycle
reach = {name: {dep for dep in defined[name] if dep in defined} for name in names}
changed = True
while changed:
    changed = False
    for name in names:
        for mid in list(reach[name]):
            for further in reach[mid]:
                if further not in reach[name]:
                    reach[name].add(further)
                    changed = True

for name in names:
    if name in reach[name]:
        errors.setdefault(name, "cycle")

changed = True
while changed:
    changed = False
    for name in names:
        if name in errors:
            continue
        failing = sorted((dep for dep in defined[name] if dep in errors), key=lambda d: d.encode())
        if failing:
            errors[name] = f"blocked:{failing[0]}"
            changed = True

loaded: list[str] = []
placed: set[str] = set()
pending = [name for name in names if name not in errors]
while pending:
    ready = [
        name
        for name in pending
        if all(dep in placed for dep in defined[name] if dep in defined)
    ]
    if not ready:
        break
    pick = min(ready, key=lambda n: n.encode())
    placed.add(pick)
    loaded.append(pick)
    pending.remove(pick)

with (OUT / "order.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("position,name\n")
    for index, name in enumerate(loaded, start=1):
        fh.write(f"{index},{name}\n")

failed = sorted((name for name in names if name in errors), key=lambda n: n.encode())
with (OUT / "errors.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("name,reason\n")
    for name in failed:
        fh.write(f"{name},{errors[name]}\n")

(OUT / "summary.json").write_text(
    json.dumps({"plugins": len(names), "loaded": len(loaded), "failed": len(failed)}) + "\n",
    encoding="utf-8",
)
