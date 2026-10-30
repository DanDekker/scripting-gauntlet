"""Grader for 258-tcl-file-literal."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "files.csv",
        ["path", "bytes", "first_line"],
        [
            ("*.cfg", 4, "cfg"),
            ("[draft].txt", 6, "draft"),
            ("nested/notes file.txt", 5, "note"),
        ],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"files": 3, "bytes": 15})
    return failures
