"""Grader for 061-retry-queue."""

import verifylib

ATTEMPTS = [
    ("steady", 1, 0),
    ("flaky", 1, 75),
    ("flaky", 2, 75),
    ("flaky", 3, 0),
    ("permanent", 1, 2),
    ("once", 1, 75),
    ("once", 2, 0),
    ("exhausted", 1, 75),
    ("exhausted", 2, 75),
    ("exhausted", 3, 75),
]
RESULTS = [
    ("steady", "ok", 1, "ready"),
    ("flaky", "ok", 3, "recovered"),
    ("permanent", "failed", 1, "bad config"),
    ("once", "ok", 2, "warmed"),
    ("exhausted", "failed", 3, "busy"),
]


def verify(io):
    failures = verifylib.table(
        io.out / "attempts.csv", ["job", "attempt", "exit_code"], ATTEMPTS
    )
    failures += verifylib.table(
        io.out / "results.csv", ["job", "status", "attempts", "message"], RESULTS
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"jobs": 5, "ok": 3, "failed": 2, "attempts": 10}
    )
    state = io.work / "attempt-state"
    for job, count in {"steady": 1, "flaky": 3, "permanent": 1, "once": 2, "exhausted": 3}.items():
        path = state / job
        if not path.is_file() or path.read_text().strip() != str(count):
            failures.append(f"worker {job}: expected {count} actual invocation(s)")
    return failures
