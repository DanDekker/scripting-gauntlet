"""Shared helpers for drill graders.

Every `verify.py` in a drill may `import verifylib` — the harness puts `harness/` on
`sys.path` before loading a grader. These helpers exist so a grader states the *contract*
in a few lines instead of re-implementing CSV and JSON comparison fifty times.

Graders still assert semantics, never bytes: numbers compare with a tolerance, and
"missing" is reported as a missing file rather than an empty one.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

TOLERANCE = 0.005


def read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    """Return (header, rows), whitespace-stripped, blank lines dropped."""
    with path.open(newline="", encoding="utf-8") as fh:
        raw = [row for row in csv.reader(fh)]
    rows = [[cell.strip() for cell in row] for row in raw if any(cell.strip() for cell in row)]
    if not rows:
        return [], []
    return rows[0], rows[1:]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _coerce(value, expected):
    if isinstance(expected, bool):
        return value
    if isinstance(expected, int):
        try:
            return int(value)
        except (TypeError, ValueError):
            return value
    if isinstance(expected, float):
        try:
            return float(value)
        except (TypeError, ValueError):
            return value
    return value


def _same(got, want) -> bool:
    if isinstance(want, float):
        return isinstance(got, float) and math.isclose(got, want, abs_tol=TOLERANCE)
    if isinstance(want, int) and isinstance(got, float):
        return got == want
    return got == want


def table(path: Path, header: list[str], rows: list[tuple], label: str | None = None) -> list[str]:
    """Compare a CSV file against an expected header and rows.

    Expected rows are tuples. A float in the expectation means "parse this cell as a
    number and compare within tolerance"; an int means the same for integers.
    """
    label = label or path.name
    if not path.is_file():
        return [f"missing {label}"]

    got_header, got_rows = read_csv(path)
    failures: list[str] = []
    if got_header != header:
        return [f"{label} header: expected {header}, got {got_header}"]

    if len(got_rows) != len(rows):
        failures.append(f"{label}: expected {len(rows)} rows, got {len(got_rows)}")

    for index, (want, got) in enumerate(zip(rows, got_rows), start=1):
        if len(got) != len(want):
            failures.append(f"{label} row {index}: expected {len(want)} fields, got {len(got)}: {got!r}")
            continue
        for column, (expected_cell, actual_cell) in enumerate(zip(want, got), start=1):
            coerced = _coerce(actual_cell, expected_cell)
            if not _same(coerced, expected_cell):
                failures.append(
                    f"{label} row {index} col {column}: expected {expected_cell!r}, got {actual_cell!r}"
                )
    return failures


def json_eq(path: Path, expected, label: str | None = None) -> list[str]:
    """Compare a JSON file against an expected object (key sets and values must match)."""
    label = label or path.name
    if not path.is_file():
        return [f"missing {label}"]
    try:
        got = read_json(path)
    except Exception as exc:
        return [f"{label} is not valid JSON: {exc}"]

    failures: list[str] = []
    if isinstance(expected, dict) and isinstance(got, dict):
        for key, want in expected.items():
            if key not in got:
                failures.append(f"{label}: missing key {key!r}")
                continue
            if not _same(_coerce(got[key], want), want):
                failures.append(f"{label}[{key!r}]: expected {want!r}, got {got[key]!r}")
        for key in got:
            if key not in expected:
                failures.append(f"{label}: unexpected key {key!r}")
        return failures
    if not _same(got, expected):
        failures.append(f"{label}: expected {expected!r}, got {got!r}")
    return failures


def lines(path: Path, expected: list[str], label: str | None = None) -> list[str]:
    """Compare a text file line by line (trailing blank lines ignored)."""
    label = label or path.name
    if not path.is_file():
        return [f"missing {label}"]
    got = path.read_text(encoding="utf-8").splitlines()
    while got and not got[-1].strip():
        got.pop()
    if got != expected:
        return [f"{label}: expected {expected!r}, got {got!r}"]
    return []
