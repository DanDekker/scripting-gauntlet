#!/usr/bin/env python3
"""Harvest TODO markers from a source tree: context decides what is a marker."""

import json
import os
from pathlib import Path

WORD = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
COMMENT_MARKERS = ("//", "/*", "#", "*", "--")
BLANKS = " \t"


def marker_at(line):
    """Index of the first TODO that is really a marker, or None."""
    start = 0
    while True:
        at = line.find("TODO", start)
        if at < 0:
            return None
        start = at + 1
        after = line[at + 4 : at + 5]
        before = line[at - 1 : at] if at else ""
        if after in WORD or before in WORD:
            continue
        prefix = line[:at]
        if not prefix.strip(BLANKS):
            return at
        head = prefix.rstrip(BLANKS)
        if head != prefix and head.endswith(COMMENT_MARKERS):
            return at


def split_owner(rest):
    """(owner, remainder) for the text sitting right after the marker."""
    owner = ""
    if rest.startswith("("):
        close = rest.find(")")
        if close > 0:
            owner = rest[1:close].strip(BLANKS)
            rest = rest[close + 1 :]
    rest = rest.strip(BLANKS)
    if rest.startswith(":"):
        rest = rest[1:].strip(BLANKS)
    if owner == "-":
        owner = ""
    return owner, rest


def harvest(path, relative):
    rows = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for number, line in enumerate(text.split("\n"), start=1):
        at = marker_at(line)
        if at is None:
            continue
        owner, body = split_owner(line[at + 4 :])
        rows.append(
            {"file": relative, "line": number, "marker": "TODO", "owner": owner, "text": body}
        )
    return rows


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    tree = in_dir / "tree"
    files = sorted(
        (path for path in tree.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(tree).as_posix(),
    )

    rows = []
    for path in files:
        rows.extend(harvest(path, path.relative_to(tree).as_posix()))
    rows.sort(key=lambda row: (row["file"], row["line"]))

    lines = ["file,line,marker,owner,text"]
    for row in rows:
        lines.append(
            f"{row['file']},{row['line']},{row['marker']},{row['owner']},{row['text']}"
        )
    (out_dir / "todos.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "files_scanned": len(files),
        "todos": len(rows),
        "owners": len({row["owner"] for row in rows if row["owner"]}),
        "orphans": sum(1 for row in rows if not row["owner"]),
        "by_marker": {"TODO": len(rows)},
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
