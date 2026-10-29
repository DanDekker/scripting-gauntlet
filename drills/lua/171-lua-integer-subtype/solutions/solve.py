#!/usr/bin/env python3
"""171-lua-integer-subtype — python mirrors Lua: floor division, floor modulo, wrapping sum."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

MASK = (1 << 64) - 1


def wrap(value: int) -> int:
    value &= MASK
    return value - (1 << 64) if value >> 63 else value


def parse(token: str):
    try:
        if token.lower().startswith(("0x", "-0x", "+0x")):
            return int(token, 16), "integer"
        if any(ch in token for ch in ".eE"):
            return float(token), "float"
        return int(token), "integer"
    except ValueError:
        return None, "invalid"


def trunc_fmod(value, divisor):
    """C fmod: the remainder takes the sign of the dividend."""
    q = int(value / divisor) if isinstance(value, float) else abs(value) // divisor * (1 if value >= 0 else -1)
    return value - q * divisor


def render(value) -> str:
    if isinstance(value, float):
        return repr(value)
    return str(value)


rows = []
integers = floats = invalid = 0
for raw in (IN / "values.txt").read_text(encoding="utf-8").splitlines():
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
    else:
        floats += 1
    rows.append(
        (
            token,
            kind,
            render(value // 7),
            render(value % 7),
            render(trunc_fmod(value, 7)),
        )
    )

with (OUT / "values.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("token,kind,quotient,remainder,fmod\n")
    for row in rows:
        fh.write(",".join(row) + "\n")

total, wrapped = 0, False
for raw in (IN / "counters.txt").read_text(encoding="utf-8").splitlines():
    token = raw.strip()
    if not token or token.startswith("#"):
        continue
    value, kind = parse(token)
    if value is None or kind != "integer":
        continue
    next_total = wrap(total + value)
    if value > 0 and next_total < total:
        wrapped = True
    total = next_total

(OUT / "counters.csv").write_text(
    f"total,total_hex,wrapped\n{total},{format(total & MASK, 'x')},{'true' if wrapped else 'false'}\n",
    encoding="utf-8",
)
(OUT / "summary.json").write_text(
    json.dumps({"rows": len(rows), "integers": integers, "floats": floats, "invalid": invalid})
    + "\n",
    encoding="utf-8",
)
