#!/usr/bin/env python3
"""Flatten a JUnit XML report: trust the <testcase> leaves, not the summary attributes."""

import csv
import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path


def local(tag: str) -> str:
    """Drop any XML namespace from an element name."""
    return tag.rsplit("}", 1)[-1]


def duration(case) -> float:
    try:
        return float((case.get("time") or "0").strip())
    except ValueError:
        return 0.0


def status(case) -> str:
    children = {local(child.tag) for child in case}
    if "error" in children:
        return "error"
    if "failure" in children:
        return "fail"
    if "skipped" in children:
        return "skip"
    return "pass"


def main() -> None:
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    root = ET.parse(in_dir / "report.xml").getroot()

    rows = []
    for suite in root.iter():
        if local(suite.tag) != "testsuite":
            continue
        suite_name = suite.get("name") or ""
        for case in suite:
            if local(case.tag) != "testcase":
                continue
            rows.append(
                (
                    suite_name,
                    case.get("classname") or "",
                    case.get("name") or "",
                    status(case),
                    duration(case),
                )
            )

    with (out_dir / "tests.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["suite", "class", "name", "status", "time"])
        for suite_name, klass, name, state, seconds in rows:
            writer.writerow([suite_name, klass, name, state, f"{seconds:.3f}"])

    total = sum(row[4] for row in rows)
    slowest = ""
    best = None
    for row in rows:  # first in document order wins a tie
        if best is None or row[4] > best:
            best, slowest = row[4], row[2]

    summary = (
        '{"tests":%d,"passed":%d,"failed":%d,"errored":%d,"skipped":%d,"time":%s,"slowest":%s}'
        % (
            len(rows),
            sum(1 for row in rows if row[3] == "pass"),
            sum(1 for row in rows if row[3] == "fail"),
            sum(1 for row in rows if row[3] == "error"),
            sum(1 for row in rows if row[3] == "skip"),
            f"{total:.3f}",
            json.dumps(slowest),
        )
    )
    (out_dir / "summary.json").write_text(summary + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
