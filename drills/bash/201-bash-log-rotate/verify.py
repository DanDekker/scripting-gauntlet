"""Grader for 201-bash-log-rotate.

Ages are counted from 2026-10-29, the `today` in policy.txt.
"""

import gzip

import verifylib

EXPECTED_ROWS = [
    ("svc-2026-01-15.log", 287, "delete"),
    ("svc-2026-03-01.log", 242, "delete"),
    ("svc-2026-08-30.log", 60, "delete"),
    ("svc-2026-09-29.log", 30, "delete"),
    ("svc-2026-10-16.log", 13, "compress"),
    ("svc-2026-10-20.log", 9, "compress"),
    ("svc-2026-10-22.log", 7, "compress"),
    ("svc-2026-10-23.log", 6, "keep"),
    ("svc-2026-10-28.log", 1, "keep"),
    ("svc-2026-10-29.log", 0, "keep"),
    ("svc-2026-11-05.log", -7, "keep"),
]

EXPECTED_SUMMARY = {"kept": 4, "compressed": 3, "deleted": 4, "ignored": 1}

EXPECTED_LOGS = {
    "svc-2026-10-23.log",
    "svc-2026-10-28.log",
    "svc-2026-10-29.log",
    "svc-2026-11-05.log",
    "svc-2026-10-16.log.gz",
    "svc-2026-10-20.log.gz",
    "svc-2026-10-22.log.gz",
}

COMPRESSED = [
    "svc-2026-10-16.log",
    "svc-2026-10-20.log",
    "svc-2026-10-22.log",
]


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "rotation.csv",
        ["file", "age_days", "action"],
        EXPECTED_ROWS,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)

    logs_dir = io.out / "logs"
    if not logs_dir.is_dir():
        failures.append("missing out/logs")
        return failures

    present = {p.name for p in logs_dir.iterdir()}
    missing = sorted(EXPECTED_LOGS - present)
    extra = sorted(present - EXPECTED_LOGS)
    if missing:
        failures.append(f"out/logs: missing {missing}")
    if extra:
        failures.append(f"out/logs: unexpected {extra}")

    for name in COMPRESSED:
        gz = logs_dir / f"{name}.gz"
        original = io.fixtures / "logs" / name
        if not gz.is_file():
            continue
        try:
            payload = gzip.decompress(gz.read_bytes())
        except OSError as exc:
            failures.append(f"out/logs/{name}.gz: not gzip ({exc})")
            continue
        if payload != original.read_bytes():
            failures.append(f"out/logs/{name}.gz: content differs from the original log")

    return failures
