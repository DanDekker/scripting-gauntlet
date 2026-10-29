#!/usr/bin/env python3
"""Check that every claim in an answer is backed by a source.

Support is containment after collapsing whitespace and lowercasing both sides — a
source that only covers the beginning of a claim is not support.
"""

import csv
import json
import os
import re
from pathlib import Path

BARE = re.compile(r"^Claim:(?P<text>.*)$")
NUMBERED = re.compile(r"^Claim[ \t]+(?P<number>[0-9]+):(?P<text>.*)$")


def squash(value):
    return " ".join(value.split()).lower()


def load_sources(path):
    sources = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if text:
            sources.append(squash(text))
    return sources


def load_claims(path):
    claims = []
    for line in path.read_text(encoding="utf-8").splitlines():
        trimmed = line.strip()
        numbered = NUMBERED.match(trimmed)
        bare = BARE.match(trimmed)
        if numbered is None and bare is None:
            continue
        position = len(claims) + 1
        if numbered is not None:
            number = int(numbered.group("number"))
            text = numbered.group("text")
        else:
            number = position
            text = bare.group("text")
        claims.append({"number": number, "text": text.strip(), "position": position})
    return claims


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    sources = load_sources(in_dir / "sources.txt")
    claims = load_claims(in_dir / "answer.md")

    rows = []
    for claim in claims:
        needle = squash(claim["text"])
        supported = bool(needle) and any(needle in source for source in sources)
        rows.append(
            (claim["number"], claim["position"], "true" if supported else "false", claim["text"])
        )
    rows.sort(key=lambda row: row[0])

    with (out_dir / "claims.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["number", "supported", "text"])
        for number, _position, supported, text in rows:
            writer.writerow([number, supported, text])

    unsupported = [row for row in rows if row[2] == "false"]
    summary = {
        "claims": len(rows),
        "supported": len(rows) - len(unsupported),
        "unsupported": len(unsupported),
        "sources": len(sources),
        "unsupported_numbers": sorted({row[0] for row in unsupported}),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
