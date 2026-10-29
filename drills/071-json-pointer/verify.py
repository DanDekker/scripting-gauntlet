"""Grader for 071-json-pointer."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "values.csv",
        ["path", "value"],
        [
            ("/user/name", "Ada"),
            ("/user/roles/1", "dev"),
            ("/user/a~1b", "slash"),
            ("/user/weird key~0", "tilde"),
            ("/items/0/id", 1),
            ("/items/1/tags/0", ""),
            ("/num", 3.5),
            ("/flag", "true"),
            ("/nil", ""),
            ("/empty", ""),
            ("/missing", ""),
            ("/items/2/id", ""),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"paths": 12, "found": 7, "missing": 5}
    )
    return failures
