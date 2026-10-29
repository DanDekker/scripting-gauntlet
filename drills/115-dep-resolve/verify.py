"""Grader for 115-dep-resolve."""

import verifylib


DEPS = [
    ("click", "satisfied", "8.1.7", ">=8.0"),
    ("django", "conflicted", "3.2.0", ">=4,<5"),
    ("flask", "satisfied", "2.0.1", "==2.0.1"),
    ("idna", "satisfied", "2.6", "==2.*"),
    ("numpy", "satisfied", "1.26.4", ""),
    ("orjson", "missing", "", "==3.9.1"),
    ("pkg", "satisfied", "1.4.0", ">=1.0"),
    ("pyyaml", "satisfied", "5.4.1", "!=6.0.0"),
    ("requests", "satisfied", "2.31.0", ">=2.28"),
    ("six", "satisfied", "1.16", ">=1.16"),
    ("urllib3", "conflicted", "1.25.11", "~=1.26"),
]


def verify(io) -> list[str]:
    failures = verifylib.table(io.out / "deps.csv", ["name", "status", "installed", "required"], DEPS)
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "requirements": 11,
            "satisfied": 8,
            "conflicted": 2,
            "missing": 1,
            "extra": 2,
            "extras": ["other", "pip"],
        },
    )
    return failures
