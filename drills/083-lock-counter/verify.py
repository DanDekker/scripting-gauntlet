"""Grader for 083-lock-counter."""

import collections

import verifylib


def verify(io):
    failures = []
    counter = io.out / "counter.txt"
    if not counter.is_file():
        return ["missing counter.txt"]
    if counter.read_text(encoding="utf-8").strip() != "200":
        failures.append(f"counter.txt: expected 200, got {counter.read_text()!r}")

    events = io.out / "events.log"
    if not events.is_file():
        failures.append("missing events.log")
    else:
        lines = [line.strip() for line in events.read_text(encoding="utf-8").splitlines() if line.strip()]
        counts = collections.Counter(lines)
        if len(lines) != 200:
            failures.append(f"events.log: expected 200 increments, got {len(lines)}")
        if set(counts) != {"0", "1", "2", "3"}:
            failures.append(f"events.log: expected worker ids 0-3, got {sorted(counts)}")
        for worker, count in sorted(counts.items()):
            if count != 50:
                failures.append(f"events.log: worker {worker} ran {count} times, expected 50")

    failures += verifylib.json_eq(
        io.out / "summary.json", {"workers": 4, "per_worker": 50, "total": 200}
    )
    return failures
