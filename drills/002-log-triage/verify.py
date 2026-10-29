"""Grader for 002-log-triage.

Expected values derived from fixtures/access.log by hand (12 records, 1 junk line) and
cross-checked against three independent solutions.
"""

import json

# count desc, then status asc (numeric)
EXPECTED_STATUS = [("200", 7), ("304", 1), ("401", 1), ("404", 1), ("500", 1), ("502", 1)]

# hits desc, then path asc (bytes)
EXPECTED_PATHS = [
    ("/api/users", 5),
    ("/index.html", 3),
    ("/robots.txt", 2),
    ("/about", 1),
    ("/api/login", 1),
]

EXPECTED_SUMMARY = {"valid": 12, "skipped": 1}


def read_csv(path, header):
    """Return (rows or None, failures)."""
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return None, [f"{path.name} is empty"]
    got_header = lines[0].strip().replace(" ", "")
    if got_header != header:
        return None, [f"{path.name} header: expected {header!r}, got {lines[0]!r}"]
    rows = []
    for lineno, line in enumerate(lines[1:], start=2):
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 2:
            return None, [f"{path.name} line {lineno}: expected 2 fields, got {len(parts)}: {line!r}"]
        try:
            rows.append((parts[0], int(parts[1])))
        except ValueError:
            return None, [f"{path.name} line {lineno}: count did not parse: {line!r}"]
    return rows, []


def verify(io):
    failures = []

    status = io.out / "status.csv"
    if not status.is_file():
        failures.append("missing out/status.csv")
    else:
        rows, problems = read_csv(status, "status,count")
        failures.extend(problems)
        if rows is not None:
            if len(rows) != len(EXPECTED_STATUS):
                failures.append(f"status.csv: expected {len(EXPECTED_STATUS)} rows, got {len(rows)}")
            for index, (want, got) in enumerate(zip(EXPECTED_STATUS, rows), start=1):
                if got[0] != want[0]:
                    failures.append(
                        f"status.csv row {index}: expected {want[0]!r}, got {got[0]!r} "
                        "(count desc, then status asc)"
                    )
                elif got[1] != want[1]:
                    failures.append(
                        f"status.csv row {index} ({got[0]}): expected {want[1]}, got {got[1]}"
                    )

    paths = io.out / "top_paths.csv"
    if not paths.is_file():
        failures.append("missing out/top_paths.csv")
    else:
        rows, problems = read_csv(paths, "path,hits")
        failures.extend(problems)
        if rows is not None:
            if len(rows) > 5:
                failures.append(f"top_paths.csv: expected at most 5 rows, got {len(rows)}")
            if len(rows) != len(EXPECTED_PATHS):
                failures.append(f"top_paths.csv: expected {len(EXPECTED_PATHS)} rows, got {len(rows)}")
            for index, (want, got) in enumerate(zip(EXPECTED_PATHS, rows), start=1):
                if got[0] != want[0]:
                    failures.append(
                        f"top_paths.csv row {index}: expected {want[0]!r}, got {got[0]!r} "
                        "(hits desc, then path asc; query strings stripped)"
                    )
                elif got[1] != want[1]:
                    failures.append(
                        f"top_paths.csv row {index} ({got[0]}): expected {want[1]} hits, got {got[1]}"
                    )

    summary = io.out / "summary.json"
    if not summary.is_file():
        failures.append("missing out/summary.json")
    else:
        try:
            got = json.loads(summary.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"summary.json is not valid JSON: {exc}")
        else:
            if not isinstance(got, dict):
                failures.append("summary.json: expected an object")
            else:
                for key, want in EXPECTED_SUMMARY.items():
                    if key not in got:
                        failures.append(f"summary.json: missing key {key!r}")
                    elif got[key] != want:
                        failures.append(f"summary.json[{key!r}]: expected {want}, got {got[key]!r}")
                for key in got:
                    if key not in EXPECTED_SUMMARY:
                        failures.append(f"summary.json: unexpected key {key!r}")

    return failures
