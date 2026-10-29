#!/usr/bin/env python3
"""Build the too-large decoy and stamp a deterministic mtime order on the tree."""

import os
import time
from pathlib import Path

inp = Path(os.environ["IN"])
base = inp / "tree" / "home" / "pp"

huge = base / "Desktop" / "budget-march-huge.csv"
huge.write_text("month,amount\n" + "2026-01,100.00\n" * 700, encoding="utf-8")

ages = {
    "Downloads/march-budget-final.csv": 2,
    "Downloads/budget-march-v2.csv": 5,
    "Desktop/march-budget.csv": 10,
    "Downloads/spreadsheet-march.csv": 20,
}
now = time.time()
for path in base.rglob("*"):
    if not path.is_file():
        continue
    relative = str(path.relative_to(base))
    days = ages.get(relative, 30)
    stamp = now - days * 86400
    os.utime(path, (stamp, stamp))
