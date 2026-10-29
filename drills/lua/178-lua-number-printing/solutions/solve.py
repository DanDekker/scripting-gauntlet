#!/usr/bin/env python3
"""178-lua-number-printing — same contract; python's repr is the same shortest-round-trip
rule Lua's tostring uses, and .17g/.6g match string.format."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])


def lua_tostring(value) -> str:
    """Lua renders a float with %.14g when that round-trips, else %.17g, and appends .0
    when the result has no decimal point or exponent."""
    if isinstance(value, int):
        return str(value)
    text = format(value, ".14g")
    if float(text) != value:
        text = format(value, ".17g")
    if not any(ch in text for ch in ".eEin"):
        text += ".0"
    return text


def parse(token: str):
    try:
        if any(ch in token for ch in ".eE"):
            return float(token), "float"
        return int(token), "integer"
    except ValueError:
        return None, "invalid"


rows = []
integers = floats = invalid = scientific = 0

for raw in (IN / "numbers.txt").read_text(encoding="utf-8").splitlines():
    token = raw.strip()
    if not token or token.startswith("#"):
        continue
    value, kind = parse(token)
    if value is None:
        invalid += 1
        rows.append((token, "invalid", "", "", ""))
        continue
    if kind == "integer":
        integers += 1
        plain = str(value)
    else:
        floats += 1
        plain = lua_tostring(value)
    if "e" in plain:
        scientific += 1
    rows.append((token, kind, plain, format(value, ".17g"), format(value, ".6g")))

with (OUT / "numbers.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("token,kind,plain,full,short\n")
    for row in rows:
        fh.write(",".join(row) + "\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "rows": len(rows),
            "integers": integers,
            "floats": floats,
            "invalid": invalid,
            "scientific": scientific,
        }
    )
    + "\n",
    encoding="utf-8",
)
