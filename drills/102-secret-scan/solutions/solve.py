#!/usr/bin/env python3
"""Scan a directory tree for hardcoded credentials: candidates first, then the filters."""

import csv
import json
import os
import re
from pathlib import Path

KEY_RE = re.compile(r"(api_key|apikey|secret|password|passwd|token)[ \t]*[:=]", re.IGNORECASE)
PLACEHOLDERS = {"changeme", "your-key-here", "xxx", "todo", "example", "<redacted>"}
MIN_LENGTH = 8
SAMPLE_SUFFIXES = (".example", ".example.txt")
SEPARATORS = " \t"


def is_sample(relative):
    return relative.endswith(SAMPLE_SUFFIXES)


def read_value(rest):
    """Take the value that follows the =/: — quoted content, else up to whitespace."""
    text = rest.lstrip(SEPARATORS)
    if text[:1] in {'"', "'"}:
        quote = text[0]
        body = text[1:]
        end = body.find(quote)
        return body if end < 0 else body[:end]
    for index, char in enumerate(text):
        if char in SEPARATORS:
            return text[:index]
    return text


def scan_file(path, relative):
    """Yield (line_number, key, value, is_secret) for every candidate line."""
    sample = is_sample(relative)
    text = path.read_text(encoding="utf-8", errors="replace")
    for number, line in enumerate(text.splitlines(), start=1):
        match = KEY_RE.search(line)
        if match is None:
            continue
        key = match.group(1)
        value = read_value(line[match.end():])
        secret = (
            not sample
            and value != ""
            and value.lower() not in PLACEHOLDERS
            and len(value) >= MIN_LENGTH
        )
        yield number, key, value, secret


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    tree = in_dir / "tree"
    if not tree.is_dir():
        raise SystemExit(f"{tree}: no such directory")

    files = sorted(
        (path, path.relative_to(tree).as_posix())
        for path in tree.rglob("*")
        if path.is_file()
    )

    findings = []
    candidates = 0
    for path, relative in files:
        for number, key, value, secret in scan_file(path, relative):
            candidates += 1
            if secret:
                findings.append((relative, number, key, value))

    findings.sort(key=lambda row: (row[0], row[1]))

    with (out_dir / "findings.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["file", "line", "key", "value"])
        writer.writerows(findings)

    summary = {
        "files_scanned": len(files),
        "candidates": candidates,
        "secrets": len(findings),
        "unique_values": len({row[3] for row in findings}),
        "sample_files": sum(1 for _, relative in files if is_sample(relative)),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
