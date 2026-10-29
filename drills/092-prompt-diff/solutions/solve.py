#!/usr/bin/env python3
"""Diff two prompt versions: normalize each line, then compare as ordered sets."""

import csv
import json
import os
import re
from pathlib import Path

GUARDRAILS = ("must", "never", "do not", "don't", "should not")
RUN_OF_WS = re.compile(r"\s+")


def normalized_lines(path):
    """Distinct normalized lines, in order of first appearance."""
    order = []
    seen = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        norm = RUN_OF_WS.sub(" ", line).strip()
        if not norm or norm in seen:
            continue
        seen.add(norm)
        order.append(norm)
    return order


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    v1 = normalized_lines(in_dir / "prompt_v1.txt")
    v2 = normalized_lines(in_dir / "prompt_v2.txt")
    v1_set, v2_set = set(v1), set(v2)

    removed = [line for line in v1 if line not in v2_set]
    added = [line for line in v2 if line not in v1_set]
    unchanged = len(v1_set & v2_set)
    guardrails = [line for line in removed if any(g in line.lower() for g in GUARDRAILS)]

    with (out_dir / "changes.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["change", "line"])
        for line in removed:
            writer.writerow(["removed", line])
        for line in added:
            writer.writerow(["added", line])

    summary = {
        "removed": len(removed),
        "added": len(added),
        "unchanged": unchanged,
        "guardrails_removed": len(guardrails),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
