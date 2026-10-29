"""Plausible percent-scaling error: 12.5% becomes 0.12."""

import csv
import os
import runpy
from pathlib import Path

drill = Path(__file__).resolve().parents[1]
runpy.run_path(str(drill / "solutions" / "solve.py"))
path = Path(os.environ["OUT"]) / "parsed.csv"
with path.open(newline="", encoding="utf-8") as fh:
    rows = list(csv.reader(fh))
rows[4][1] = "0.12"
with path.open("w", newline="", encoding="utf-8") as fh:
    csv.writer(fh).writerows(rows)
