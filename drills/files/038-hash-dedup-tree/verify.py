"""Grader for 038-hash-dedup-tree.

fixtures/tree holds 11 files: three copies of the 167-byte report, two copies each of
the 67-byte config and the 60-byte todo, one zero-byte placeholder, and four distinct
files. 4 duplicates, 461 wasted bytes, 6 distinct hashes among the 10 non-empty files.
"""

import verifylib

REPORT = "2594802e24d214c5903f828084ffd0afc7cf7ad45822ab70b3cde98d66618cb8"
CONFIG = "06619da03852562891f8f698102df1c0173efc20816cd53fabf202188747336e"
TODO = "aa81d53868bc7b5184bd6b38efb9b6a9713f050562b4dca14935bb1404e9beeb"

ROWS = [
    ("config/app.ini", "config/app.ini.bak", CONFIG, 67),
    ("docs/report.txt", "archive/2024/report-final.txt", REPORT, 167),
    ("docs/report.txt", "docs/report-copy.txt", REPORT, 167),
    ("notes/todo.md", "backup/todo (1).md", TODO, 60),
]


def verify(io):
    failures = verifylib.table(
        io.out / "dupes.csv", ["keeper", "duplicate", "sha256", "bytes"], ROWS
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "files": 11,
            "unique_hashes": 6,
            "duplicate_files": 4,
            "wasted_bytes": 461,
            "empty": 1,
        },
    )
    return failures
