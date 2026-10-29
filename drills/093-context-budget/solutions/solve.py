#!/usr/bin/env python3
"""Greedy context packer: dedupe last-wins, order by priority then path, fill."""

import csv
import json
import os
import re
from pathlib import Path

TOKENS_OK = re.compile(r"^[0-9]+$")
PRIORITY_OK = re.compile(r"^-?[0-9]+$")


def read_candidates(path):
    """path -> (tokens, priority); the last valid row for a path wins."""
    table = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.reader(fh):
            if len(row) < 3:
                continue
            name, tokens, priority = (cell.strip() for cell in row[:3])
            if not name:
                continue
            if not TOKENS_OK.match(tokens) or not PRIORITY_OK.match(priority):
                continue
            table[name] = (int(tokens), int(priority))
    return table


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    table = read_candidates(in_dir / "files.csv")
    budget = int((in_dir / "budget.txt").read_text(encoding="utf-8").strip())

    order = sorted(table.items(), key=lambda item: (item[1][1], item[0]))

    included = []
    included_tokens = 0
    remaining = budget
    skipped = 0
    for name, (tokens, _priority) in order:
        if tokens <= remaining:
            included.append(name)
            included_tokens += tokens
            remaining -= tokens
        else:
            skipped += 1

    (out_dir / "context.txt").write_text(
        "".join(name + "\n" for name in included), encoding="utf-8"
    )

    summary = {
        "budget": budget,
        "included": len(included),
        "included_tokens": included_tokens,
        "skipped": skipped,
        "remaining": remaining,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
