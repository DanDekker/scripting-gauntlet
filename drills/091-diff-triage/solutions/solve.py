#!/usr/bin/env python3
"""Triage a unified diff: per-file churn plus every risk flag that applies."""

import csv
import json
import os
import re
from pathlib import Path

SECRET_MARKERS = ("api_key", "api-key", "password", "secret", "-----begin")
LARGE_THRESHOLD = 100
FLAGS = ["binary", "deleted", "large", "mode-change", "new", "secret"]


def parse_diff(text):
    files = []
    current = None
    for line in text.splitlines():
        if line.startswith("diff --git "):
            current = {"path": None, "added": 0, "deleted": 0, "binary": False,
                       "new": False, "deleted_file": False, "mode": False, "secret": False}
            files.append(current)
            header = line[len("diff --git "):]
            # a/<path> b/<path>
            parts = header.split(" ")
            for part in parts:
                if part.startswith("b/"):
                    current["path"] = part[2:]
            continue
        if current is None:
            continue
        if line.startswith("Binary files "):
            current["binary"] = True
            continue
        if line.startswith("new file mode "):
            current["new"] = True
            continue
        if line.startswith("deleted file mode "):
            current["deleted_file"] = True
            continue
        if line.startswith("old mode ") or line.startswith("new mode "):
            current["mode"] = True
            continue
        if line.startswith("--- "):
            if line[4:].strip() == "/dev/null":
                current["new"] = True
            continue
        if line.startswith("+++ "):
            side = line[4:].strip()
            if side == "/dev/null":
                current["deleted_file"] = True
            else:
                if side.startswith("b/"):
                    side = side[2:]
                current["path"] = side
            continue
        if line.startswith("+"):
            current["added"] += 1
            lowered = line.lower()
            if any(marker in lowered for marker in SECRET_MARKERS):
                current["secret"] = True
            continue
        if line.startswith("-"):
            current["deleted"] += 1
            continue
    return files


def flags_for(record):
    flags = []
    if record["binary"]:
        flags.append("binary")
    if record["deleted_file"]:
        flags.append("deleted")
    if record["added"] + record["deleted"] >= LARGE_THRESHOLD:
        flags.append("large")
    if record["mode"]:
        flags.append("mode-change")
    if record["new"]:
        flags.append("new")
    if record["secret"]:
        flags.append("secret")
    return flags


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    text = (in_dir / "changes.diff").read_text(encoding="utf-8")
    records = parse_diff(text)

    rows = []
    for record in records:
        rows.append(
            {
                "path": record["path"] or "",
                "added": record["added"],
                "deleted": record["deleted"],
                "flags": ";".join(flags_for(record)),
            }
        )
    rows.sort(key=lambda row: row["path"])

    with (out_dir / "risk.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["path", "added", "deleted", "flags"])
        for row in rows:
            writer.writerow([row["path"], row["added"], row["deleted"], row["flags"]])

    flagged = [row for row in rows if row["flags"]]
    top_risk = ""
    best = -1
    for row in sorted(rows, key=lambda r: r["path"]):
        count = len(row["flags"].split(";")) if row["flags"] else 0
        if count > best:
            best = count
            top_risk = row["path"]
    if best <= 0:
        top_risk = ""

    summary = {
        "files": len(rows),
        "total_added": sum(row["added"] for row in rows),
        "total_deleted": sum(row["deleted"] for row in rows),
        "flagged_files": len(flagged),
        "top_risk": top_risk,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
