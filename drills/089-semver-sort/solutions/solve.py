#!/usr/bin/env python3
import json
import os
import re
import sys
from functools import cmp_to_key
from pathlib import Path

SEMVER_RE = re.compile(
    r"^[vV]?(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def parse_semver(tag):
    m = SEMVER_RE.match(tag.strip())
    if not m:
        return None
    major = int(m.group("major"))
    minor = int(m.group("minor"))
    patch = int(m.group("patch"))
    pre = m.group("prerelease")
    return {
        "tag": tag.strip(),
        "major": major,
        "minor": minor,
        "patch": patch,
        "prerelease": pre.split(".") if pre else None,
    }


def compare_pre_id(a, b):
    a_is_num = a.isdigit()
    b_is_num = b.isdigit()
    if a_is_num and b_is_num:
        ai, bi = int(a), int(b)
        return (ai > bi) - (ai < bi)
    if a_is_num and not b_is_num:
        return -1
    if not a_is_num and b_is_num:
        return 1
    return (a > b) - (a < b)


def compare_semver(a, b):
    for k in ("major", "minor", "patch"):
        if a[k] != b[k]:
            return (a[k] > b[k]) - (a[k] < b[k])
    pa = a["prerelease"]
    pb = b["prerelease"]
    if pa is None and pb is None:
        return 0
    if pa is None and pb is not None:
        return 1
    if pa is not None and pb is None:
        return -1
    for ida, idb in zip(pa, pb):
        c = compare_pre_id(ida, idb)
        if c != 0:
            return c
    return (len(pa) > len(pb)) - (len(pa) < len(pb))


def main():
    indir = Path(os.environ["IN"])
    outdir = Path(os.environ["OUT"])
    outdir.mkdir(parents=True, exist_ok=True)

    lines = [line.strip() for line in (indir / "tags.txt").read_text(encoding="utf-8").splitlines()]
    non_empty = [line for line in lines if line]

    valid = []
    for item in non_empty:
        parsed = parse_semver(item)
        if parsed is not None:
            valid.append(parsed)

    # Python sort is stable
    valid.sort(key=cmp_to_key(compare_semver))

    (outdir / "sorted.txt").write_text("\n".join(v["tag"] for v in valid) + "\n", encoding="utf-8")

    stables = [v["tag"] for v in valid if v["prerelease"] is None]
    latest_stable = stables[-1] if stables else None
    latest_overall = valid[-1]["tag"] if valid else None

    summary = {
        "total_lines": len(non_empty),
        "valid_count": len(valid),
        "latest_stable": latest_stable,
        "latest_overall": latest_overall,
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
