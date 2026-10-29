#!/usr/bin/env python3
"""Run a review checklist over a unified diff: five independent rules, added lines only."""

import csv
import json
import os
import re
from pathlib import Path

CODE_ORDER = ("debug", "hardcoded-endpoint", "long-line", "todo", "trailing-whitespace")
IPV4 = re.compile(r"(?<![\d.])(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(?![\d.])")


def has_ipv4(text: str) -> bool:
    for match in IPV4.finditer(text):
        if all(int(part) <= 255 for part in match.groups()):
            return True
    return False


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = (in_dir / "changes.diff").read_text(encoding="utf-8").splitlines()

    files = []
    findings = []
    added = 0
    current = ""

    for number, line in enumerate(lines, start=1):
        if line.startswith("diff --git "):
            header = line[len("diff --git a/") :]
            cut = header.find(" b/")
            current = header[cut + 3 :] if cut >= 0 else header
            if current not in files:
                files.append(current)
            continue
        if line.startswith("+++ "):
            side = line[4:]
            if side != "/dev/null":
                current = side[2:] if side.startswith("b/") else side
            continue
        if not line.startswith("+"):
            continue

        added += 1
        body = line[1:]
        if line[-1] in " \t":
            findings.append((current, number, "trailing-whitespace"))
        if len(line) > 100:
            findings.append((current, number, "long-line"))
        if "TODO" in body or "FIXME" in body:
            findings.append((current, number, "todo"))
        if "console.log" in body or "print(" in body:
            findings.append((current, number, "debug"))
        if "http://" in body or "https://" in body or has_ipv4(body):
            findings.append((current, number, "hardcoded-endpoint"))

    findings.sort()
    with (out_dir / "findings.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["file", "line", "code"])
        writer.writerows(findings)

    by_code = {}
    for code in CODE_ORDER:
        count = sum(1 for finding in findings if finding[2] == code)
        if count:
            by_code[code] = count

    summary = {
        "files": len(files),
        "lines_added": added,
        "findings": len(findings),
        "by_code": by_code,
        "files_flagged": len({finding[0] for finding in findings}),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, separators=(",", ":")) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
