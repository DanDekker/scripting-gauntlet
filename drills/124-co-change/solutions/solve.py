#!/usr/bin/env python3
"""Find the file pairs that always change together: count commits, not lines."""

import json
import os
import sys
from itertools import combinations
from pathlib import Path


def commit_sets(path):
    """Return one set of distinct paths per commit block, in log order."""
    blocks = []
    current = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line == "commit" or line.startswith("commit "):
            current = set()
            blocks.append(current)
            continue
        if current is None:
            continue  # anything before the first commit line is ignored
        if line:
            current.add(line)
    return blocks


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    log = in_dir / "log.txt"
    if not log.is_file():
        sys.exit(f"missing {log}")
    out_dir.mkdir(parents=True, exist_ok=True)

    commits = commit_sets(log)

    touched = {}
    shared = {}
    for files in commits:
        for name in files:
            touched[name] = touched.get(name, 0) + 1
        for a, b in combinations(sorted(files), 2):
            shared[(a, b)] = shared.get((a, b), 0) + 1

    rows = []
    for (a, b), count in shared.items():
        if count < 2:
            continue
        score = count / (touched[a] + touched[b] - count)
        rows.append((a, b, count, score, round(score, 4)))
    rows.sort(key=lambda row: (-row[2], -row[4], row[0], row[1]))

    lines = ["file_a,file_b,shared,score"]
    for a, b, count, score, _ in rows:
        lines.append(f"{a},{b},{count},{score:.4f}")
    (out_dir / "pairs.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "commits": sum(1 for files in commits if files),
        "files": len(touched),
        "coupled_pairs": len(rows),
        "most_coupled": rows[0][0] if rows else "",
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
