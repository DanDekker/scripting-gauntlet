#!/usr/bin/env python3
"""168-ruby-truthiness — same contract; python has the same falsy set (None/False), so
the rule is stated explicitly rather than inferred from `or`."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

base = json.loads((IN / "base.json").read_text(encoding="utf-8"))
override = json.loads((IN / "override.json").read_text(encoding="utf-8"))

merged = dict(base)
removed = from_override = 0

for key, value in override.items():
    if value is None:
        removed += 1
        merged.pop(key, None)
    else:
        merged[key] = value
        from_override += 1

rows = []
for key in sorted(merged, key=lambda item: item.encode()):
    value = merged[key]
    if isinstance(value, bool):
        kind, text = "bool", "true" if value else "false"
    elif isinstance(value, int):
        kind, text = "int", str(value)
    elif isinstance(value, float):
        kind, text = "float", repr(value)
    else:
        kind, text = "string", value
    rows.append((key, kind, text))

with (OUT / "merged.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("key,type,value\n")
    for row in rows:
        fh.write(",".join(row) + "\n")

(OUT / "summary.json").write_text(
    json.dumps({"keys": len(merged), "from_override": from_override, "removed": removed})
    + "\n",
    encoding="utf-8",
)
