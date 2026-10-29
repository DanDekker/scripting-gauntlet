#!/usr/bin/env python3
"""Changelog: group the conventional commits, drop the rest, keep the trailers honest."""

import json
import os
import re
from pathlib import Path

CONVENTIONAL = re.compile(
    r"^(feat|fix|docs|refactor|perf|test|chore|build|ci)(\([^)]*\))?(!)?: (?P<subject>.*)$"
)
TRAILER = "BREAKING CHANGE:"
INTERNAL = {"chore", "build", "ci", "test"}
SECTIONS = [
    ("Features", "feat"),
    ("Bug Fixes", "fix"),
    ("Performance", "perf"),
    ("Refactoring", "refactor"),
    ("Documentation", "docs"),
]


def main() -> None:
    inp = Path(os.environ["IN"])
    out = Path(os.environ["OUT"])
    out.mkdir(parents=True, exist_ok=True)

    source = inp / "commits.txt"
    if not source.is_file():
        raise SystemExit(f"missing input: {source}")

    entries: list[dict] = []
    previous: int | None = None
    commits = conventional = skipped = 0

    for raw in source.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(TRAILER):
            if previous is not None:
                entries[previous]["breaking"] = True
            continue
        commits += 1
        match = CONVENTIONAL.match(line)
        if match is None:
            skipped += 1
            previous = None
            continue
        conventional += 1
        entries.append(
            {
                "type": match.group(1),
                "subject": match.group("subject"),
                "breaking": bool(match.group(3)),
            }
        )
        previous = len(entries) - 1

    blocks: list[str] = []
    for name, kind in SECTIONS:
        items = [entry["subject"] for entry in entries if entry["type"] == kind]
        if items:
            blocks.append("\n".join([f"## {name}", *[f"- {item}" for item in items]]))
    broken = [entry["subject"] for entry in entries if entry["breaking"]]
    if broken:
        blocks.append("\n".join(["## Breaking Changes", *[f"- {item}" for item in broken]]))

    (out / "changelog.md").write_text("\n\n".join(blocks) + "\n", encoding="utf-8")

    summary = {
        "commits": commits,
        "conventional": conventional,
        "skipped": skipped,
        "internal": sum(1 for entry in entries if entry["type"] in INTERNAL),
        "breaking": len(broken),
        "features": sum(1 for entry in entries if entry["type"] == "feat"),
        "fixes": sum(1 for entry in entries if entry["type"] == "fix"),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
