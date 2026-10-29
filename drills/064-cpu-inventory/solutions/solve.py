#!/usr/bin/env python3
"""Normalize Linux, macOS and Windows CPU reports."""

import csv
import json
import os
from pathlib import Path

root = Path(os.environ["IN"])
out = Path(os.environ["OUT"])


def read_fields(path):
    fields = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def arch(value):
    value = value.lower()
    if "arm64" in value or "aarch64" in value:
        return "arm64"
    if any(mark in value for mark in ("x64", "amd64", "x86_64")):
        return "x86_64"
    raise SystemExit(f"unknown architecture: {value}")


linux = read_fields(root / "linux" / "lscpu.txt")
mac = read_fields(root / "macos" / "sysctl.txt")
windows = json.loads((root / "windows" / "system.json").read_text(encoding="utf-8"))
linux_cores = int(linux["Core(s) per socket"]) * int(linux["Socket(s)"])
linux_threads = int(linux["CPU(s)"])
mac_cores = int(mac["hw.physicalcpu"])
mac_threads = int(mac["hw.logicalcpu"])
win_cores = sum(int(cpu["NumberOfCores"]) for cpu in windows["processors"])
win_threads = sum(int(cpu["NumberOfLogicalProcessors"]) for cpu in windows["processors"])
rows = [
    ("linux", linux["Model name"], linux_cores, linux_threads, linux_threads // linux_cores, arch(linux["Architecture"])),
    ("macos", mac["machdep.cpu.brand_string"], mac_cores, mac_threads, mac_threads // mac_cores, arch((root / "macos/uname.txt").read_text().strip())),
    ("windows", windows["processors"][0]["Name"], win_cores, win_threads, win_threads // win_cores, arch(windows["CsSystemType"])),
]
with (out / "cpus.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.writer(stream)
    writer.writerow(["platform", "processor", "physical_cores", "logical_cpus", "threads_per_core", "architecture"])
    writer.writerows(sorted(rows))
(out / "summary.json").write_text(
    json.dumps({"hosts": 3, "physical_cores": linux_cores + mac_cores + win_cores,
                "logical_cpus": linux_threads + mac_threads + win_threads}) + "\n",
    encoding="utf-8",
)
