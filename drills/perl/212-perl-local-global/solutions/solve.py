#!/usr/bin/env python3
"""212-perl-local-global — python twin with one module-level setting."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

# The one separator setting, shared by the render helper.
SEP = ","


def render(kind: str, value: str) -> str:
    return SEP.join([kind, value])


records = []
for line in (IN / "records.txt").read_text(encoding="utf-8").splitlines():
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    kind, _, value = line.strip().partition(" ")
    records.append((kind, value))

rendered = []
wide = 0
for kind, value in records:
    if kind == "wide":
        wide += 1
        # Override the setting for this record only, then put it back.
        saved = SEP
        SEP = ";"
        try:
            rendered.append(render(kind, value))
        finally:
            SEP = saved
    else:
        rendered.append(render(kind, value))

(OUT / "report.txt").write_text(
    "".join(line + "\n" for line in rendered), encoding="utf-8"
)

(OUT / "summary.json").write_text(
    json.dumps(
        {"records": len(records), "wide": wide, "sep_after": SEP},
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
