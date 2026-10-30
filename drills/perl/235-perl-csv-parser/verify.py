"""Grader for 235-perl-csv-parser.

Verifies RFC 4180 CSV parsing, unescaping, and malformed row detection.
"""

from pathlib import Path
import verifylib

EXPECTED_ROWS = [
    ("101", "Acme Corp", "Widget, Deluxe", "199.99", "rush order"),
    ("102", "Smith, John", "Standard Bolt", "4.50", 'pickup at "Warehouse A"'),
    ("103", "Beta LLC", "Anchor", "45.00", ""),
    ("104", "Doe, Jane", "Cable, 10ft", "25.50", "handle with care"),
    ("106", "O'Reilly, Tim", 'Manual, "Perl Tips"', "50.00", "gift wrapped"),
]

EXPECTED_SUMMARY = {
    "total_rows": 6,
    "valid": 5,
    "malformed": 1,
    "total_amount": 324.99,
}


def verify(io):
    failures = []
    tsv_path = io.out / "clean.tsv"
    if not tsv_path.is_file():
        return ["missing clean.tsv"]

    lines = tsv_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return ["clean.tsv is empty"]

    header = lines[0].split("\t")
    expected_header = ["order_id", "customer", "product", "amount", "notes"]
    if header != expected_header:
        failures.append(f"clean.tsv header: expected {expected_header}, got {header}")

    data_rows = [tuple(line.split("\t")) for line in lines[1:] if line.strip()]
    if len(data_rows) != len(EXPECTED_ROWS):
        failures.append(f"clean.tsv: expected {len(EXPECTED_ROWS)} rows, got {len(data_rows)}")
    else:
        for idx, (exp, got) in enumerate(zip(EXPECTED_ROWS, data_rows), start=1):
            if exp != got:
                failures.append(f"clean.tsv row {idx}: expected {exp}, got {got}")

    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
