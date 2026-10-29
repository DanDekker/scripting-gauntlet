#!/usr/bin/env python3
"""Normalize three captured native OS identity reports."""

import csv
import json
import os
from pathlib import Path

root = Path(os.environ["IN"])
out = Path(os.environ["OUT"])


def require(path):
    if not path.is_file():
        raise SystemExit(f"missing input: {path}")
    return path.read_text(encoding="utf-8").strip()


def linux_value(path, key):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit(f"missing {key} in {path}")


def colon_value(path, key):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.split(":", 1)[0].strip() == key:
            return line.split(":", 1)[1].strip()
    raise SystemExit(f"missing {key} in {path}")


def arch(value):
    value = value.lower()
    if "arm64" in value or "aarch64" in value:
        return "arm64"
    if any(token in value for token in ("x64", "amd64", "x86_64")):
        return "x86_64"
    raise SystemExit(f"unknown architecture: {value}")


linux = root / "linux"
macos = root / "macos"
windows = json.loads(require(root / "windows" / "computer.json"))
rows = [
    (
        "linux",
        require(linux / "hostname.txt"),
        linux_value(linux / "os-release", "NAME"),
        linux_value(linux / "os-release", "VERSION_ID"),
        arch(require(linux / "uname.txt")),
    ),
    (
        "macos",
        require(macos / "hostname.txt"),
        colon_value(macos / "sw_vers.txt", "ProductName"),
        colon_value(macos / "sw_vers.txt", "ProductVersion"),
        arch(require(macos / "uname.txt")),
    ),
    (
        "windows",
        windows["CsName"],
        windows["WindowsProductName"],
        windows["WindowsVersion"],
        arch(windows["CsSystemType"]),
    ),
]
with (out / "hosts.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.writer(stream)
    writer.writerow(["platform", "hostname", "name", "version", "architecture"])
    writer.writerows(sorted(rows))
(out / "summary.json").write_text(json.dumps({"platforms": len(rows)}) + "\n", encoding="utf-8")
