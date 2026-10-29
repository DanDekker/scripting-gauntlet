"""Plausible wrong solver: correct totals, wrong requested row order."""

import os
import runpy
from pathlib import Path

drill = Path(__file__).resolve().parents[1]
runpy.run_path(str(drill / "solutions" / "solve.py"))
output = Path(os.environ["OUT"]) / "regions.csv"
header, *rows = output.read_text(encoding="utf-8").splitlines()
output.write_text("\n".join([header, *sorted(rows)]) + "\n", encoding="utf-8")
