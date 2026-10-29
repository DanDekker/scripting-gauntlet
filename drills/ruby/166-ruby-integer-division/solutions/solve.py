#!/usr/bin/env python3
"""166-ruby-integer-division — same contract; python's divmod also floors, so the
interesting part is stating the rule, not the operator."""

import json
import os
from collections import defaultdict
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

sums: dict[str, int] = defaultdict(int)
counts: dict[str, int] = defaultdict(int)

for raw in (IN / "balances.csv").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    account, _, delta = line.partition(",")
    if account == "account":
        continue
    sums[account] += int(delta)
    counts[account] += 1

rows = []
for account in sorted(sums):
    quotient, remainder = divmod(sums[account], counts[account])
    rows.append((account, sums[account], counts[account], quotient, remainder))

with (OUT / "averages.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("account,sum,count,avg_cents,carry\n")
    for row in rows:
        fh.write(",".join(str(cell) for cell in row) + "\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "accounts": len(sums),
            "total": sum(sums.values()),
            "negative_accounts": sum(1 for value in sums.values() if value < 0),
        }
    )
    + "\n",
    encoding="utf-8",
)
