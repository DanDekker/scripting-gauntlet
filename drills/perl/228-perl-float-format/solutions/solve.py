#!/usr/bin/env python3
"""228-perl-float-format — python twin.

Python's format() already rounds a midpoint to even, but its default str() keeps a
trailing .0 and round-trips the shortest representation, so the plain column has to
emulate perl's 15-significant-digit printing.
"""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])


def perl_plain(value: float) -> str:
    """Perl prints a number in string context with 15 significant digits."""
    return format(value, ".15g")


rows = []
total = 0.0
max_value = None

for line in (IN / "amounts.txt").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    label, _, amount = line.partition(" ")
    amount = amount.strip()

    value = float(amount)
    total += value
    if max_value is None or value > max_value:
        max_value = value

    rows.append(
        (
            label,
            perl_plain(value),
            format(value, ".2f"),
            format(value, ".0f"),
        )
    )

with (OUT / "amounts.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("label,plain,cents,whole\n")
    for row in rows:
        fh.write(",".join(row) + "\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "amounts": len(rows),
            "total_cents": format(total, ".2f"),
            "max_plain": perl_plain(max_value),
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
