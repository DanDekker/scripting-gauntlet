#!/usr/bin/env bash
set -euo pipefail

in_tags="$IN/tags.txt"
out_sorted="$OUT/sorted.txt"
out_summary="$OUT/summary.json"

python3 - << 'EOF'
import sys, os, json, re
from functools import cmp_to_key

in_tags = os.environ["IN"] + "/tags.txt"
out_sorted = os.environ["OUT"] + "/sorted.txt"
out_summary = os.environ["OUT"] + "/summary.json"

SEMVER_RE = re.compile(
    r"^[vV]?(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

def parse(tag):
    m = SEMVER_RE.match(tag.strip())
    if not m: return None
    pre = m.group("prerelease")
    return {
        "tag": tag.strip(),
        "major": int(m.group("major")),
        "minor": int(m.group("minor")),
        "patch": int(m.group("patch")),
        "pre": pre.split(".") if pre else None
    }

def cmp_id(a, b):
    if a.isdigit() and b.isdigit():
        ai, bi = int(a), int(b)
        return (ai > bi) - (ai < bi)
    if a.isdigit(): return -1
    if b.isdigit(): return 1
    return (a > b) - (a < b)

def cmp_ver(a, b):
    for k in ("major", "minor", "patch"):
        if a[k] != b[k]:
            return (a[k] > b[k]) - (a[k] < b[k])
    pa, pb = a["pre"], b["pre"]
    if pa is None and pb is None: return 0
    if pa is None: return 1
    if pb is None: return -1
    for ida, idb in zip(pa, pb):
        c = cmp_id(ida, idb)
        if c != 0: return c
    return (len(pa) > len(pb)) - (len(pa) < len(pb))

with open(in_tags, encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]

valid = [p for p in (parse(l) for l in lines) if p is not None]
valid.sort(key=cmp_to_key(cmp_ver))

with open(out_sorted, "w", encoding="utf-8") as f:
    for v in valid:
        f.write(v["tag"] + "\n")

stables = [v["tag"] for v in valid if v["pre"] is None]
summary = {
    "total_lines": len(lines),
    "valid_count": len(valid),
    "latest_stable": stables[-1] if stables else None,
    "latest_overall": valid[-1]["tag"] if valid else None
}
with open(out_summary, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)
    f.write("\n")
EOF
