"""Grader for 004-scrape-table."""

import csv

EXPECTED = [
    ("Enterprise", 500, 2499.00),
    ("Scale & Co", 100, 749.00),
    ("Team", 25, 199.00),
    ("Starter", 5, 49.00),
]

TOLERANCE = 0.005


def verify(io):
    path = io.out / "pricing.csv"
    if not path.is_file():
        return ["missing out/pricing.csv"]

    failures = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        rows = [row for row in reader if any(cell.strip() for cell in row)]

    if not rows:
        return ["out/pricing.csv is empty"]

    header = [cell.strip() for cell in rows[0]]
    if header != ["plan", "seats", "monthly_usd"]:
        failures.append(f"header: expected ['plan', 'seats', 'monthly_usd'], got {rows[0]!r}")
        return failures

    data = rows[1:]
    if len(data) != len(EXPECTED):
        failures.append(f"expected {len(EXPECTED)} plan rows, got {len(data)}")
        return failures

    for index, (want, got) in enumerate(zip(EXPECTED, data), start=1):
        if len(got) != 3:
            failures.append(f"row {index}: expected 3 fields, got {len(got)}: {got!r}")
            continue
        plan, seats, price = got[0].strip(), got[1].strip(), got[2].strip()
        want_plan, want_seats, want_price = want

        if plan != want_plan:
            failures.append(
                f"row {index}: expected plan {want_plan!r}, got {plan!r} "
                "(check entity decoding, badge removal, and sort order)"
            )
        try:
            got_seats = int(seats)
        except ValueError:
            failures.append(f"row {index} ({plan!r}): seats did not parse: {seats!r}")
            continue
        if got_seats != want_seats:
            failures.append(f"row {index} ({plan!r}): expected {want_seats} seats, got {got_seats}")

        try:
            got_price = float(price)
        except ValueError:
            failures.append(f"row {index} ({plan!r}): price did not parse: {price!r}")
            continue
        if abs(got_price - want_price) > TOLERANCE:
            failures.append(
                f"row {index} ({plan!r}): expected {want_price:.2f}, got {got_price:.2f}"
            )

    return failures
