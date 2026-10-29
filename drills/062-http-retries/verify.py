"""Grader for 062-http-retries."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "results.csv",
        ["endpoint", "status", "attempts", "http_code", "items"],
        [
            ("steady", "ok", 1, 200, 2),
            ("flaky", "ok", 3, 200, 3),
            ("gone", "failed", 1, 404, ""),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"endpoints": 3, "ok": 2, "failed": 1, "requests": 5}
    )
    hits = io.work / "hits.log"
    if not hits.is_file():
        failures.append("mock server received no requests")
    else:
        want = ["steady", "flaky", "flaky", "flaky", "gone"]
        got = hits.read_text(encoding="utf-8").splitlines()
        if got != want:
            failures.append(f"HTTP request order/count: expected {want}, got {got}")
    return failures
