"""Grader for 131-port-scan-triage.

Expected values read by hand off fixtures/scan.txt + fixtures/baseline.csv: 17 non-blank
lines, 2 skipped, 15 valid lines -> 25 records (the range line expands to 11), 3 of them
superseded, 22 distinct (port, protocol) pairs. 18 stay open, 13 are unbaselined, and 4
need attention (443 unexpected, 8080 unexpected, 6379 should-be-closed, 9000
wrong-service).
"""

import verifylib

RANGE = [(port, "tcp", "open", "zmq", "unbaselined") for port in range(8000, 8011)]

ROWS = [
    (22, "tcp", "open", "ssh", "ok"),
    (53, "tcp", "filtered", "", "unbaselined"),
    (53, "udp", "open", "domain", "unbaselined"),
    (80, "tcp", "open", "http", "ok"),
    (443, "tcp", "closed", "", "unexpected"),
    (3306, "tcp", "open", "mysql", "ok"),
    (5432, "tcp", "open", "postgres", "ok"),
    (6379, "tcp", "open", "redis", "should-be-closed"),
    *RANGE,
    (8080, "tcp", "filtered", "", "unexpected"),
    (8443, "tcp", "closed", "", "ok"),
    (9000, "tcp", "open", "", "wrong-service"),
]

SUMMARY = {
    "lines": 17,
    "ports": 22,
    "skipped": 2,
    "superseded": 3,
    "open": 18,
    "unbaselined": 13,
    "attention": 4,
}


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "ports.csv", ["port", "proto", "state", "service", "verdict"], ROWS
    )
    failures += verifylib.json_eq(io.out / "summary.json", SUMMARY)
    return failures
