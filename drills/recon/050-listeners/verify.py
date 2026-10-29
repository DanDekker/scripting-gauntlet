"""Grader for 050-listeners.

Expected values read by hand off fixtures/netstat-an.txt: 23 tcp rows, 10 of them LISTEN,
which collapse to 9 distinct (port,address) listeners, 2 of which are shadowed.
"""

import verifylib

# port asc (numeric), then address asc (bytes)
LISTENERS = [
    (22, "*"),
    (631, "*"),
    (5432, "127.0.0.1"),
    (5432, "::1"),
    (8080, "*"),
    (8080, "127.0.0.1"),
    (9000, "*"),
    (9090, "*"),
    (9090, "192.168.1.50"),
]

CONFLICTS = [
    (8080, "127.0.0.1"),
    (9090, "192.168.1.50"),
]

SUMMARY = {"tcp_rows": 23, "listeners": 9, "conflicts": 2}


def verify(io):
    failures = verifylib.table(io.out / "listeners.csv", ["port", "address"], LISTENERS)
    failures += verifylib.table(io.out / "conflicts.csv", ["port", "address"], CONFLICTS)
    failures += verifylib.json_eq(io.out / "summary.json", SUMMARY)
    return failures
