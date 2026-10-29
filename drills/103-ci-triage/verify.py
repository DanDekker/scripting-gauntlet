"""Grader for 103-ci-triage."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "results.csv",
        ["test", "verdict"],
        [
            ("tests/test_api.py::test_legacy", "skip"),
            ("tests/test_api.py::test_ping", "pass"),
            ("tests/test_api.py::test_timeout", "pass"),
            ("tests/test_cache.py::test_evict", "fail"),
            ("tests/test_db.py::test_seed", "error"),
            ("tests/test_db.py::test_setup", "error"),
            ("tests/test_queue.py::test_ack", "pass"),
            ("tests/test_queue.py::test_drain", "fail"),
            ("tests/test_render.py::test_html", "skip"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"tests": 9, "passed": 3, "failed": 2, "errored": 2, "skipped": 2},
    )
    return failures
