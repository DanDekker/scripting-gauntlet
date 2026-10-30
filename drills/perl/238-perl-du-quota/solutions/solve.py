#!/usr/bin/env python3
import json
import re
from pathlib import Path


def parse_bytes(s: str) -> int:
    s = s.strip()
    m = re.match(r"^([0-9]+(?:\.[0-9]+)?)\s*([kmgtb]?)$", s, re.IGNORECASE)
    if not m:
        raise ValueError(f"Invalid size: {s}")
    val_str, unit_raw = m.groups()
    val = float(val_str)
    unit = unit_raw.lower() if unit_raw else ""
    mult = 1
    if unit == "k":
        mult = 1024
    elif unit == "m":
        mult = 1024 * 1024
    elif unit == "g":
        mult = 1024 * 1024 * 1024
    elif unit == "t":
        mult = 1024 * 1024 * 1024 * 1024
    return int(round(val * mult))


quotas = {}
quotas_file = Path("in/quotas.tsv")
for line in quotas_file.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    parts = line.split("\t")
    if parts[0] == "path":
        continue
    quotas[parts[0]] = parse_bytes(parts[1])

default_quota = quotas.get("DEFAULT")
if default_quota is None:
    raise ValueError("Missing DEFAULT quota")

alerts = []
total_checked = 0
total_overage = 0

usage_file = Path("in/usage.txt")
for line in usage_file.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    parts = line.split("\t")
    if len(parts) < 2:
        continue
    size_str, path = parts[0], parts[1]
    total_checked += 1
    usage_bytes = parse_bytes(size_str)
    quota_bytes = quotas.get(path, default_quota)

    if usage_bytes > quota_bytes:
        overage = usage_bytes - quota_bytes
        pct = f"{(usage_bytes / quota_bytes) * 100:.1f}"
        alerts.append({
            "path": path,
            "usage_bytes": usage_bytes,
            "quota_bytes": quota_bytes,
            "overage_bytes": overage,
            "pct_used": pct,
        })
        total_overage += overage

alerts.sort(key=lambda a: (-a["overage_bytes"], a["path"]))

out_dir = Path("out")
out_dir.mkdir(parents=True, exist_ok=True)

tsv_lines = ["path\tusage_bytes\tquota_bytes\toverage_bytes\tpct_used"]
for a in alerts:
    tsv_lines.append(f"{a['path']}\t{a['usage_bytes']}\t{a['quota_bytes']}\t{a['overage_bytes']}\t{a['pct_used']}")
Path("out/alerts.tsv").write_text("\n".join(tsv_lines) + "\n", encoding="utf-8")

top_offender = alerts[0]["path"] if alerts else ""

summary = {
    "over_quota_count": len(alerts),
    "top_offender": top_offender,
    "total_checked": total_checked,
    "total_overage_bytes": total_overage,
}

Path("out/summary.json").write_text(json.dumps(summary, separators=(",", ":")), encoding="utf-8")
