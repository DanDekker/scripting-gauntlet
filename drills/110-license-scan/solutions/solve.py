#!/usr/bin/env python3
"""Check a dependency list against the licences the policy allows.

Three outcomes per dependency: allowed, denied, unknown. An unlisted licence is unknown,
not denied.
"""

import csv
import json
import os
import re
from pathlib import Path

SUFFIX = re.compile(r"[ \t]*license$")


def normalise(value):
    text = value.strip().lower()
    text = SUFFIX.sub("", text)
    return text.strip()


def load_policy(path):
    policy = {}
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    for row in rows[1:]:
        cells = [cell.strip() for cell in row]
        if not any(cells):
            continue
        allowed = cells[1].lower() if len(cells) > 1 else ""
        policy[normalise(cells[0])] = "yes" if allowed == "yes" else "no"
    return policy


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    policy = load_policy(in_dir / "policy.csv")

    deps = []
    skipped = 0
    for line in (in_dir / "deps.txt").read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) == 4 and fields[3].lower() == "license":
            fields = [fields[0], fields[1], fields[2] + " " + fields[3]]
        if len(fields) != 3:
            skipped += 1
            continue
        name, version, licence = fields[0], fields[1], normalise(fields[2])
        if licence not in policy:
            status = "unknown"
        else:
            status = "allowed" if policy[licence] == "yes" else "denied"
        deps.append({"name": name, "version": version, "licence": licence, "status": status})

    versions = {}
    for dep in deps:
        versions.setdefault(dep["name"], set()).add(dep["version"])
    conflicts = sum(1 for seen in versions.values() if len(seen) > 1)

    deps.sort(key=lambda dep: (dep["name"], dep["version"]))

    with (out_dir / "deps.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["name", "version", "licence", "status"])
        for dep in deps:
            writer.writerow([dep["name"], dep["version"], dep["licence"], dep["status"]])

    summary = {
        "deps": len(deps),
        "skipped": skipped,
        "allowed": sum(1 for dep in deps if dep["status"] == "allowed"),
        "denied": sum(1 for dep in deps if dep["status"] == "denied"),
        "unknown": sum(1 for dep in deps if dep["status"] == "unknown"),
        "conflicts": conflicts,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
