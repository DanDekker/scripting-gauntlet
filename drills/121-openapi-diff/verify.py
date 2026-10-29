"""Grader for 121-openapi-diff."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "changes.csv",
        ["path", "method", "code"],
        [
            ("/health", "get", "required-param-added"),
            ("/legacy", "get", "removed"),
            ("/metrics", "get", "operation-id-changed"),
            ("/metrics", "get", "required-param-added"),
            ("/reports", "get", "param-removed"),
            ("/reports", "get", "required-param-added"),
            ("/teams/{id}", "post", "added"),
            ("/users", "get", "operation-id-changed"),
            ("/users", "get", "required-param-added"),
            ("/users", "put", "added"),
            ("/users/", "get", "removed"),
            ("/users/lookup", "get", "added"),
            ("/users/{id}", "delete", "removed"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "endpoints_old": 9,
            "endpoints_new": 9,
            "added": 3,
            "removed": 3,
            "breaking": 9,
            "safe": 4,
            "changed_endpoints": 4,
        },
    )
    return failures
