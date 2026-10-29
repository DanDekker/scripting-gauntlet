"""Plausible left-join error: omit a right-only key."""

import csv
import os
import runpy
from pathlib import Path

drill = Path(__file__).resolve().parents[1]
runpy.run_path(str(drill / "solutions" / "solve.py"))
path = Path(os.environ["OUT"]) / "joined.csv"
with path.open(newline="", encoding="utf-8") as fh:
    rows = list(csv.reader(fh))
rows = [row for row in rows if row[0] != "d-500"]
with path.open("w", newline="", encoding="utf-8") as fh:
    csv.writer(fh).writerows(rows)
