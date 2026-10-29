"""Grader for 128-listing-scrape."""

import verifylib

ROWS = [
    ("Widget & Co", "12.50", "/p/1"),
    ("Gadget <Pro>", "1299.00", "https://example.com/p/2"),
    ("Sprocket", "7.00", ""),
    ("Bracket", "", ""),
    ("Mug 'n' Cup", "2.50", "/p/6/"),
    ('Gasket "Heavy"', "4.25", "/p/7"),
    ("Gasket Insert 'inner'", "1.10", "/p/8"),
    ("Hinge", "5.00", "/p/10"),
    ("Cable", "", "/p/11"),
]

SUMMARY = {
    "items": 12,
    "kept": 9,
    "skipped": 2,
    "duplicates": 1,
    "priced": 7,
    "unpriced": 2,
    "total": 1331.35,
}


def verify(io) -> list[str]:
    failures = verifylib.table(io.out / "items.csv", ["name", "price", "link"], ROWS)
    failures += verifylib.json_eq(io.out / "summary.json", SUMMARY)
    return failures
