"""Grader for 051-conn-states.

Hand-counted from fixtures/netstat-an.txt: 23 tcp data rows, 10 LISTEN + 13 connections,
5 distinct states, peers 93.184.216.34 x5 and 140.82.114.4 x4 leading.
"""

import verifylib

# count desc, then state asc (bytes)
STATES = [
    ("LISTEN", 10),
    ("ESTABLISHED", 9),
    ("TIME_WAIT", 2),
    ("CLOSE_WAIT", 1),
    ("FIN_WAIT_2", 1),
]

# connections desc, then remote asc (bytes), top 3
REMOTES = [
    ("93.184.216.34", 5),
    ("140.82.114.4", 4),
    ("1.1.1.1", 1),
]

SUMMARY = {"tcp_rows": 23, "connections": 13, "states": 5}


def verify(io):
    failures = verifylib.table(io.out / "states.csv", ["state", "count"], STATES)
    failures += verifylib.table(io.out / "remote_top.csv", ["remote", "connections"], REMOTES)
    failures += verifylib.json_eq(io.out / "summary.json", SUMMARY)
    return failures
