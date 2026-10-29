#!/usr/bin/env python3
"""Catalogue unresolved merge-conflict blocks under in/repo/."""

import json
import os
from pathlib import Path


def scan(text):
    """Return (start, end, ours, theirs, our_lines, their_lines) for complete blocks."""
    blocks = []
    state = 0  # 0 idle, 1 ours, 2 base, 3 theirs
    start = end = 0
    ours = theirs = ""
    our_lines = their_lines = 0
    for number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("<<<<<<< "):
            state = 1
            start = number
            ours = line[8:].strip()
            our_lines = their_lines = 0
            continue
        if state == 1:
            if line.startswith("||||||| "):
                state = 2
            elif line.rstrip() == "=======":
                state = 3
            else:
                our_lines += 1
            continue
        if state == 2:
            if line.rstrip() == "=======":
                state = 3
            continue
        if state == 3:
            if line.startswith(">>>>>>> "):
                end = number
                theirs = line[8:].strip()
                blocks.append((start, end, ours, theirs, our_lines, their_lines))
                state = 0
            else:
                their_lines += 1
    return blocks


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    root = in_dir / "repo"
    scanned = 0
    conflicted = set()
    rows = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if not path.is_file():
                continue
            scanned += 1
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            relative = path.relative_to(root).as_posix()
            for block in scan(text):
                conflicted.add(relative)
                rows.append((relative,) + block)

    rows.sort(key=lambda row: (row[0], row[1]))

    lines = ["file,start_line,end_line,our_branch,their_branch,our_lines,their_lines"]
    widest = 0
    for row in rows:
        widest = max(widest, row[5] + row[6])
        lines.append(",".join(str(cell) for cell in row))
    (out_dir / "conflicts.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "files_scanned": scanned,
        "conflicted_files": len(conflicted),
        "total_conflicts": len(rows),
        "clean_files": scanned - len(conflicted),
        "max_conflict_lines": widest,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
