#!/usr/bin/env python3
"""169-ruby-sort-mixed — same contract; python's sort is stable, but the index is still
carried so the rule does not depend on that guarantee."""

import json
import os
import re
from pathlib import Path

NUMERIC = re.compile(r"^-?[0-9]+(\.[0-9]+)?$")

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

records = []
lines = invalid = 0

for raw in (IN / "records.jsonl").read_text(encoding="utf-8").splitlines():
    text = raw.strip()
    if not text:
        continue
    lines += 1
    record = json.loads(text)
    name = record.get("name")
    score = record.get("score")
    if score is None:
        records.append((name, None, len(records)))
    elif isinstance(score, str) and not NUMERIC.match(score):
        invalid += 1
    else:
        records.append((name, float(score), len(records)))

ranked = sorted(
    records,
    key=lambda item: (item[1] is None, 0.0 if item[1] is None else -item[1], item[2]),
)

def score_text(value):
    if value is None:
        return ""
    return str(int(value)) if value.is_integer() else repr(value)

with (OUT / "ranked.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("rank,name,score\n")
    for position, (name, score, _index) in enumerate(ranked, start=1):
        fh.write(f"{position},{name},{score_text(score)}\n")

missing = sum(1 for _name, score, _index in records if score is None)
(OUT / "summary.json").write_text(
    json.dumps(
        {"lines": lines, "ranked": len(ranked), "invalid": invalid, "missing": missing}
    )
    + "\n",
    encoding="utf-8",
)
