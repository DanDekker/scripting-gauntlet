#!/usr/bin/env python3
"""Portable property-list reference for the macOS privacy audit."""

import json
import os
import plistlib
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

with (inp / "apps.plist").open("rb") as source:
    records = plistlib.load(source)["Apps"]

apps = []
skipped = 0
for record in records:
    ident = record.get("CFBundleIdentifier")
    version = record.get("CFBundleShortVersionString")
    if not isinstance(ident, str) or not isinstance(version, str):
        skipped += 1
        continue
    ident, version = ident.strip(), version.strip()
    if not ident or not version:
        skipped += 1
        continue
    permissions = []
    for key, label in (
        ("NSCameraUsageDescription", "camera"),
        ("NSMicrophoneUsageDescription", "microphone"),
    ):
        purpose = record.get(key)
        if isinstance(purpose, str) and purpose.strip():
            permissions.append(label)
    if permissions:
        apps.append({"id": ident, "version": version, "permissions": permissions})

apps.sort(key=lambda app: app["id"])
(out / "report.json").write_text(
    json.dumps({"apps": apps, "skipped": skipped}) + "\n", encoding="utf-8"
)
