#!/usr/bin/env python3
"""Resolve declared requirements against the installed world."""

import csv
import json
import os
import re
from pathlib import Path

REQUIREMENT = re.compile(r"^([A-Za-z0-9_.-]+)(?:\[[^\]]*\])?\s*(.*)$")
OPERATORS = ("==", "!=", ">=", "<=", "~=", ">", "<")


def parts(version):
    return [int(piece) for piece in version.split(".")]


def compare(left, right):
    """Component-wise integer compare; the shorter side is zero-padded."""
    a, b = parts(left), parts(right)
    width = max(len(a), len(b))
    a += [0] * (width - len(a))
    b += [0] * (width - len(b))
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


def prefix_match(prefix, version):
    p, v = parts(prefix), parts(version)
    return len(v) >= len(p) and v[: len(p)] == p


def specifier_matches(specifier, version):
    for op in OPERATORS:
        if specifier.startswith(op):
            value = specifier[len(op):].strip()
            break
    else:
        return False

    star = value.endswith(".*")
    if star:
        value = value[:-2]

    if op == "==":
        return prefix_match(value, version) if star else compare(value, version) == 0
    if op == "!=":
        return not prefix_match(value, version) if star else compare(value, version) != 0
    if op == ">=":
        return compare(version, value) >= 0
    if op == ">":
        return compare(version, value) > 0
    if op == "<=":
        return compare(version, value) <= 0
    if op == "<":
        return compare(version, value) < 0
    # ~=: at least the given version, and the same prefix minus its last component.
    if compare(version, value) < 0:
        return False
    fixed = parts(value)[:-1]
    return not fixed or prefix_match(".".join(str(n) for n in fixed), version)


def specifiers_match(spec, version):
    return all(
        specifier_matches(piece.strip(), version)
        for piece in spec.split(",")
        if piece.strip()
    )


def load_installed(path):
    installed = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) < 2 or line.lstrip().startswith("#"):
            continue
        installed.setdefault(fields[0], fields[1])
    return installed


def load_requirements(path):
    requirements = []
    seen = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ";" in line:
            continue
        cut = line.find("#")
        if cut >= 0:
            line = line[:cut].strip()
        if not line:
            continue
        match = REQUIREMENT.match(line)
        if not match:
            continue
        name = match.group(1)
        if name in seen:
            continue
        seen.add(name)
        requirements.append((name, match.group(2).strip()))
    return requirements


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    installed = load_installed(in_dir / "installed.txt")
    requirements = load_requirements(in_dir / "requirements.txt")

    rows = []
    counts = {"satisfied": 0, "conflicted": 0, "missing": 0}
    for name, spec in sorted(requirements, key=lambda item: item[0]):
        version = installed.get(name, "")
        if not version:
            status = "missing"
        elif not spec or specifiers_match(spec, version):
            status = "satisfied"
        else:
            status = "conflicted"
        counts[status] += 1
        rows.append((name, status, version, spec))

    with (out_dir / "deps.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["name", "status", "installed", "required"])
        writer.writerows(rows)

    required_names = {name for name, _ in requirements}
    extras = sorted(name for name in installed if name not in required_names)
    summary = {
        "requirements": len(requirements),
        "satisfied": counts["satisfied"],
        "conflicted": counts["conflicted"],
        "missing": counts["missing"],
        "extra": len(extras),
        "extras": extras,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
