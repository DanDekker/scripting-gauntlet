"""Grader for 199-ruby-forwardable-delegation.

Expected audit rows:
Step 8: delete disk is blocked with NoMethodError
Step 9: get disk still succeeds with 500 because deletion was prevented
"""

import verifylib

EXPECTED = [
    (1, "add", "ok", "cpu=4"),
    (2, "add", "ok", "mem=16"),
    (3, "get", "ok", "4"),
    (4, "add", "ok", "disk=500"),
    (5, "get", "ok", "16"),
    (6, "size", "ok", "3"),
    (7, "keys", "ok", "cpu;disk;mem"),
    (8, "delete", "blocked", "NoMethodError"),
    (9, "get", "ok", "500"),
]

EXPECTED_SUMMARY = {"steps": 9, "reads": 3, "blocked": 1, "final_size": 3}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "audit.csv",
        ["step", "op", "status", "result"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
