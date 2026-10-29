#!/usr/bin/env python3
"""031-rank-ties — sort once, then walk the scores tracking the previous value."""

import csv
import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

players = []
with (inp / "scores.csv").open(newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh)
    next(reader, None)
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue
        name, score = (cell.strip() for cell in (row + [""] * 2)[:2])
        players.append((name, int(score)))

players.sort(key=lambda p: (-p[1], p[0]))

ranked = []
previous = None
dense = 0
for position, (name, score) in enumerate(players, start=1):
    if score != previous:
        dense += 1
        rank = position
    previous = score
    ranked.append((name, score, rank, dense))

with (out / "ranked.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh, lineterminator="\n")
    writer.writerow(["name", "score", "rank", "dense_rank"])
    writer.writerows(ranked)

summary = {
    "players": len(ranked),
    "top_score": ranked[0][1] if ranked else 0,
    "distinct_scores": dense,
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
