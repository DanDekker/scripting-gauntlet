"""Plausible locale error: parse the ambiguous slash date as day first."""

import csv
import os
import runpy
from pathlib import Path

drill = Path(__file__).resolve().parents[1]
runpy.run_path(str(drill / "solutions" / "solve.py"))
path = Path(os.environ["OUT"]) / "normalised.csv"
with path.open(newline="", encoding="utf-8") as fh:
    rows = list(csv.reader(fh))
rows[8][1] = "2026-02-01"
with path.open("w", newline="", encoding="utf-8") as fh:
    csv.writer(fh).writerows(rows)
