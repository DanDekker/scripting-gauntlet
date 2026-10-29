"""Plausible cumulative-rounding error: 33.33 + 33.33 becomes 66.66."""

import csv
import os
import runpy
from pathlib import Path

drill = Path(__file__).resolve().parents[1]
runpy.run_path(str(drill / "solutions" / "solve.py"))
path = Path(os.environ["OUT"]) / "shares.csv"
with path.open(newline="", encoding="utf-8") as fh:
    rows = list(csv.reader(fh))
rows[5][4] = "66.66"
with path.open("w", newline="", encoding="utf-8") as fh:
    csv.writer(fh).writerows(rows)
