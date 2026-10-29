"""Verifier for 089-semver-sort."""

import json
from pathlib import Path
import verifylib


def verify(io) -> list[str]:
    sorted_file = io.out / "sorted.txt"
    summary_file = io.out / "summary.json"

    failures = []
    if not sorted_file.is_file():
        return ["missing sorted.txt"]
    if not summary_file.is_file():
        return ["missing summary.json"]

    expected_sorted = [
        "0.9.0-rc.1",
        "V0.9.0",
        "1.0.0-alpha",
        "v1.0.0-alpha.1",
        "1.0.0-alpha.1+build.1",
        "1.0.0-alpha.1+build.2",
        "1.0.0-alpha.beta",
        "1.0.0-beta",
        "1.0.0-beta.2",
        "1.0.0-beta.11",
        "1.0.0-rc.1",
        "v1.0.0",
        "1.0.0+20130313144700",
        "v1.0.0+exp.sha.5114f85",
        "v2.0.0-rc.1",
        "2.0.0",
    ]

    got_sorted = [line.strip() for line in sorted_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    if got_sorted != expected_sorted:
        failures.append(f"sorted.txt mismatch: expected {expected_sorted}, got {got_sorted}")

    expected_summary = {
        "total_lines": 20,
        "valid_count": 16,
        "latest_stable": "2.0.0",
        "latest_overall": "2.0.0",
    }
    failures.extend(verifylib.json_eq(summary_file, expected_summary))

    return failures
