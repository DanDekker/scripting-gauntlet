"""Grader for 244-ps1-literal-pattern."""

import verifylib


def verify(io):
    return verifylib.keyed_table(
        io.out / "matches.csv",
        ["name", "rule", "match"],
        [
            ("api.v2", "api.v2", "yes"),
            ("apiXv2", "api.v2", "no"),
            ("worker+", "worker+", "yes"),
            ("worker", "worker+", "no"),
            ("cache[1]", "cache[1]", "yes"),
            ("cache1", "cache[1]", "no"),
            ("proxy?", "proxy?", "yes"),
            ("proxyX", "proxy?", "no"),
            ("API.V2", "api.v2", "no"),
            ("web", "web", "yes"),
        ],
    ) + verifylib.json_eq(
        io.out / "summary.json",
        {"matched": 5, "unmatched": 5},
    )
