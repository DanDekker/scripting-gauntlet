#!/usr/bin/env python3
"""Compare benchmark sample medians and apply a regression threshold."""

import csv
import json
import os
import statistics
from collections import defaultdict
from pathlib import Path

root = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
sets = {}
for name in ("baseline", "candidate"):
    grouped = defaultdict(list)
    with (root / f"{name}.csv").open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            try:
                value = float(row["ms"])
            except (KeyError, ValueError) as exc:
                raise SystemExit(f"bad timing in {name}.csv: {row}") from exc
            if value <= 0:
                raise SystemExit(f"non-positive timing in {name}.csv: {row}")
            grouped[(row["platform"], row["case"])].append(value)
    for key, values in grouped.items():
        if len(values) != 3:
            raise SystemExit(f"expected three samples for {key} in {name}.csv")
    sets[name] = grouped
if sets["baseline"].keys() != sets["candidate"].keys():
    raise SystemExit("baseline and candidate platform/case pairs differ")

rows = []
regressions = 0
for platform, case in sorted(sets["baseline"]):
    before = statistics.median(sets["baseline"][(platform, case)])
    after = statistics.median(sets["candidate"][(platform, case)])
    change = round((after - before) / before * 100, 1)
    status = "regression" if change > 10.0 else "ok"
    regressions += status == "regression"
    rows.append((platform, case, before, after, change, status))
with (out / "comparison.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.writer(stream)
    writer.writerow(["platform", "case", "baseline_median_ms", "candidate_median_ms", "change_pct", "status"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps({"comparisons": len(rows), "regressions": regressions, "threshold_pct": 10}) + "\n",
    encoding="utf-8",
)
