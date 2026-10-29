"""Grader for 124-co-change."""

import csv

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "pairs.csv",
        ["file_a", "file_b", "shared", "score"],
        [
            ("src/export.py", "src/users.py", 4, 0.6667),
            ("src/export.py", "src/report.py", 4, 0.5714),
            ("src/report.py", "src/users.py", 3, 0.5),
            ("src/billing.py", "src/report.py", 2, 0.3333),
            ("src/billing.py", "src/export.py", 2, 0.2857),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"commits": 8, "files": 5, "coupled_pairs": 5, "most_coupled": "src/export.py"},
    )
    # A pair must appear once, with the smaller path in file_a.
    if (io.out / "pairs.csv").is_file():
        _, rows = verifylib.read_csv(io.out / "pairs.csv")
        seen = set()
        for row in rows:
            if len(row) != 4:
                continue
            if row[0] >= row[1]:
                failures.append(f"pairs.csv: file_a must sort before file_b, got {row[0]!r},{row[1]!r}")
            if (row[0], row[1]) in seen:
                failures.append(f"pairs.csv: duplicate pair {row[0]!r},{row[1]!r}")
            seen.add((row[0], row[1]))
    return failures
