"""Grader for 001-csv-rollup.

Expected values are derived from fixtures/orders.csv by hand and cross-checked against
three independent solutions (python, bash/awk, lua). Assert semantics: parsed numbers,
region order, key presence — never a byte diff.
"""

import json

# (region, orders, revenue) in the contract's order: revenue desc, ties region asc.
EXPECTED_ROWS = [
    ("North", 2, 1500.00),
    ("East", 1, 1100.00),
    ("South", 2, 975.75),
    ("West", 2, 100.00),
]

EXPECTED_SUMMARY = {"orders": 7, "regions": 4, "revenue": 3675.75, "dropped": 1}

TOLERANCE = 0.005


def check_regions(path):
    failures = []
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return ["out/regions.csv is empty"]

    header = lines[0].strip().replace(" ", "")
    if header != "region,orders,revenue":
        failures.append(f"regions.csv header: expected 'region,orders,revenue', got {lines[0]!r}")

    rows = []
    for lineno, line in enumerate(lines[1:], start=2):
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 3:
            failures.append(f"regions.csv line {lineno}: expected 3 fields, got {len(parts)}: {line!r}")
            continue
        try:
            rows.append((parts[0], int(parts[1]), float(parts[2])))
        except ValueError:
            failures.append(f"regions.csv line {lineno}: numbers did not parse: {line!r}")

    if len(rows) != len(EXPECTED_ROWS):
        failures.append(f"regions.csv: expected {len(EXPECTED_ROWS)} data rows, got {len(rows)}")
        return failures

    for index, (want, got) in enumerate(zip(EXPECTED_ROWS, rows), start=1):
        want_region, want_orders, want_revenue = want
        got_region, got_orders, got_revenue = got
        if got_region != want_region:
            failures.append(
                f"regions.csv row {index}: expected {want_region!r}, got {got_region!r} "
                "(rows must be revenue desc, ties by region asc)"
            )
        if got_orders != want_orders:
            failures.append(
                f"regions.csv row {index} ({got_region}): expected {want_orders} orders, got {got_orders}"
            )
        if abs(got_revenue - want_revenue) > TOLERANCE:
            failures.append(
                f"regions.csv row {index} ({got_region}): expected revenue {want_revenue:.2f}, "
                f"got {got_revenue:.2f}"
            )
    return failures


def check_summary(path):
    failures = []
    try:
        got = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"out/summary.json is not valid JSON: {exc}"]
    if not isinstance(got, dict):
        return [f"out/summary.json: expected an object, got {type(got).__name__}"]

    for key, want in EXPECTED_SUMMARY.items():
        if key not in got:
            failures.append(f"summary.json: missing key {key!r}")
            continue
        have = got[key]
        if isinstance(want, float):
            if not isinstance(have, (int, float)) or isinstance(have, bool):
                failures.append(f"summary.json[{key!r}]: expected a number, got {have!r}")
            elif abs(float(have) - want) > TOLERANCE:
                failures.append(f"summary.json[{key!r}]: expected {want}, got {have!r}")
        elif have != want:
            failures.append(f"summary.json[{key!r}]: expected {want!r}, got {have!r}")

    for key in got:
        if key not in EXPECTED_SUMMARY:
            failures.append(f"summary.json: unexpected key {key!r}")
    return failures


def verify(io):
    regions = io.out / "regions.csv"
    summary = io.out / "summary.json"
    if not regions.is_file() and not summary.is_file():
        return ["missing out/regions.csv and out/summary.json"]

    failures = []
    if not regions.is_file():
        failures.append("missing out/regions.csv")
    else:
        failures.extend(check_regions(regions))
    if not summary.is_file():
        failures.append("missing out/summary.json")
    else:
        failures.extend(check_summary(summary))
    return failures
