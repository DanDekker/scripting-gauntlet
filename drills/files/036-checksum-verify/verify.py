"""Grader for 036-checksum-verify.

Expected rows are the contract in PROMPT.md applied to fixtures/: the signed manifest
was taken when app.conf still ended at `log_level`, logs/app.log existed, and
data/scratch.tmp did not.
"""

import verifylib

ROWS = [
    (
        "README.md",
        "MATCH",
        "e9ffbb913173004f3ec115fb843ff746b8f2a7eccd6adc4274e01ca4d03648ca",
        "e9ffbb913173004f3ec115fb843ff746b8f2a7eccd6adc4274e01ca4d03648ca",
    ),
    (
        "app.conf",
        "MODIFIED",
        "157bb4f4a3258255d1c1a83d8923d68972f77508981d728f38121c198f2cecce",
        "e4aa7aacd499c6c89c72dea8f3eafb5aa1cea734e8640471b595f943b5480346",
    ),
    (
        "bin/run.sh",
        "MATCH",
        "bc0cc77ff40c818ac9c04ca3bc1814d6bd541532747a25e239f94b8cced774ec",
        "bc0cc77ff40c818ac9c04ca3bc1814d6bd541532747a25e239f94b8cced774ec",
    ),
    (
        "data/metrics.csv",
        "MATCH",
        "8198e1c2973b870ae6a4e6cc94d340c1ca113ac3c2458bad52e29bc5f5b10427",
        "8198e1c2973b870ae6a4e6cc94d340c1ca113ac3c2458bad52e29bc5f5b10427",
    ),
    (
        "data/scratch.tmp",
        "EXTRA",
        "",
        "a38dc6c6caedc7353b33e8dc3d1d51b65deb97a45a6557682ee4205573fd80d9",
    ),
    (
        "logs/app.log",
        "MISSING",
        "98b2d04f87f2c4d9cdfe639a86e4edbe789d8817351f74ab4fe860933a5a87ca",
        "",
    ),
    (
        "notes/meeting notes.txt",
        "MATCH",
        "1697732e817f9b2e8c67c254e1b1f286e2f7f83eb12628af6d8379f3fdf7adb4",
        "1697732e817f9b2e8c67c254e1b1f286e2f7f83eb12628af6d8379f3fdf7adb4",
    ),
]

REBUILT = [
    "e9ffbb913173004f3ec115fb843ff746b8f2a7eccd6adc4274e01ca4d03648ca  README.md",
    "e4aa7aacd499c6c89c72dea8f3eafb5aa1cea734e8640471b595f943b5480346  app.conf",
    "bc0cc77ff40c818ac9c04ca3bc1814d6bd541532747a25e239f94b8cced774ec  bin/run.sh",
    "8198e1c2973b870ae6a4e6cc94d340c1ca113ac3c2458bad52e29bc5f5b10427  data/metrics.csv",
    "a38dc6c6caedc7353b33e8dc3d1d51b65deb97a45a6557682ee4205573fd80d9  data/scratch.tmp",
    "1697732e817f9b2e8c67c254e1b1f286e2f7f83eb12628af6d8379f3fdf7adb4  notes/meeting notes.txt",
]


def verify(io):
    failures = verifylib.table(
        io.out / "verify.csv", ["path", "status", "expected", "actual"], ROWS
    )
    failures += verifylib.lines(io.out / "rebuilt.sha256", REBUILT)
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"manifest": 6, "match": 4, "missing": 1, "modified": 1, "extra": 1, "ok": False},
    )
    return failures
