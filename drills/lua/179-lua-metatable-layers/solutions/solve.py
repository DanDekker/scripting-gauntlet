#!/usr/bin/env python3
"""179-lua-metatable-layers — same contract; a chain of dicts stands in for __index."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

layers: dict[str, dict[str, str]] = {}
order: list[str] = []

for raw in (IN / "layers.txt").read_text(encoding="utf-8").splitlines():
    text = raw.strip()
    if not text or text.startswith("#"):
        continue
    name = None
    if text.startswith("layer "):
        name = text.split(None, 1)[1].strip()
        order.append(name)
        layers[name] = {}
    else:
        key, _, value = text.partition("=")
        layers[order[-1]][key.strip()] = value.strip()


def resolve(layer_name: str, key: str):
    for name in reversed(order[: order.index(layer_name) + 1]):
        if key in layers[name]:
            return layers[name][key], name
    return None, None


rows = []
resolved = absent = 0
for raw in (IN / "lookups.txt").read_text(encoding="utf-8").splitlines():
    text = raw.strip()
    if not text or text.startswith("#"):
        continue
    layer_name, key = text.split()
    value, source = resolve(layer_name, key)
    if value is None:
        rows.append((layer_name, key, "", "absent", "false"))
        absent += 1
    else:
        rows.append((layer_name, key, value, source, "true" if source == layer_name else "false"))
        resolved += 1

with (OUT / "lookups.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("layer,key,value,source,own\n")
    for row in rows:
        fh.write(",".join(row) + "\n")

with (OUT / "own_keys.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("layer,keys\n")
    for name in sorted(layers):
        fh.write(f"{name},{';'.join(sorted(layers[name]))}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {"layers": len(layers), "lookups": len(rows), "resolved": resolved, "absent": absent}
    )
    + "\n",
    encoding="utf-8",
)
