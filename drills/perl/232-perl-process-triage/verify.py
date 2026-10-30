"""Grader for 232-perl-process-triage.

Verifies process table parsing with space-carrying commands and threshold triage.
"""

import verifylib

EXPECTED = [
    (1150, "app", 95.2, 256000, "cpu", "/usr/bin/perl /opt/worker/job.pl --queue high"),
    (1042, "postgres", 85.0, 1480000, "both", "postgres: writer process"),
    (1200, "backup", 82.0, 1100000, "both", "/usr/bin/tar -czf /backup/data.tar.gz /var/data"),
    (1160, "redis", 2.1, 1200000, "memory", "/usr/bin/redis-server 127.0.0.1:6379"),
]

EXPECTED_SUMMARY = {
    "total_processes": 7,
    "flagged": 4,
    "cpu_only": 1,
    "mem_only": 1,
    "both": 2,
}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "runaways.csv",
        ["pid", "user", "cpu", "rss", "flag", "command"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
