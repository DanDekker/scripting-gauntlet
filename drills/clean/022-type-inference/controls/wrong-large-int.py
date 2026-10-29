"""Plausible type inference error: reclassify a large integer as float."""

import csv
import os
import runpy
from pathlib import Path

drill = Path(__file__).resolve().parents[1]
runpy.run_path(str(drill / "solutions" / "solve.py"))
path = Path(os.environ["OUT"]) / "types.csv"
with path.open(newline="", encoding="utf-8") as fh:
    rows = list(csv.reader(fh))
rows[3][1] = "float"
with path.open("w", newline="", encoding="utf-8") as fh:
    csv.writer(fh).writerows(rows)
