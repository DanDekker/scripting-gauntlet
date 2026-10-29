#!/usr/bin/env python3
"""Walk a markdown tree and classify every inline link: ok / broken / missing-anchor / empty."""

import csv
import json
import os
import re
from pathlib import Path

HEADING = re.compile(r"^(#+) (.*)$")
NL = re.compile(r"^\n$")


def anchors_of(path):
    found = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = HEADING.match(line.rstrip("\r"))
        if not match or len(match.group(1)) > 6:
            continue
        text = match.group(2).strip()
        if not text:
            continue
        found.add(re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-"))
    return found


def targets_in(line):
    """Yield every `](target)` target on a line, left to right."""
    position = 0
    while True:
        open_at = line.find("](", position)
        if open_at < 0:
            return
        start = open_at + 2
        close_at = line.find(")", start)
        if close_at < 0:
            return
        yield line[start:close_at]
        position = close_at + 1


def classify(rel, target, docs, anchors):
    """Return (status, external)."""
    target = target.strip()
    if not target:
        return "empty", False
    if target.startswith(("http://", "https://", "mailto:")):
        return None, True

    path, _, fragment = target.partition("#")
    if not path:
        own = anchors.get(rel, set())
        return ("ok" if fragment in own else "missing-anchor"), False

    resolved = os.path.normpath(
        os.path.join(os.path.dirname(rel), path.replace("%20", " "))
    ).replace(os.sep, "/")
    if not (docs / resolved).exists():
        return "broken", False
    if not fragment:
        return "ok", False
    return ("ok" if fragment in anchors.get(resolved, set()) else "missing-anchor"), False


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    docs = in_dir / "docs"
    files = sorted(
        (p.relative_to(docs).as_posix() for p in docs.rglob("*.md") if p.is_file()),
        key=lambda name: name.encode(),
    )
    anchors = {rel: anchors_of(docs / rel) for rel in files}

    rows = []
    counts = {"ok": 0, "broken": 0, "missing-anchor": 0, "empty": 0}
    external = 0

    for rel in files:
        in_fence = False
        for lineno, line in enumerate((docs / rel).read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for target in targets_in(line):
                status, is_external = classify(rel, target, docs, anchors)
                if is_external:
                    external += 1
                    continue
                counts[status] += 1
                rows.append((rel, str(lineno), target.strip(), status))

    with (out_dir / "links.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["file", "line", "target", "status"])
        writer.writerows(rows)

    summary = {
        "files": len(files),
        "links": len(rows),
        "ok": counts["ok"],
        "broken": counts["broken"],
        "missing_anchor": counts["missing-anchor"],
        "empty": counts["empty"],
        "external": external,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
