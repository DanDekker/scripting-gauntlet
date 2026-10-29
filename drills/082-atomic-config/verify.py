"""Grader for 082-atomic-config."""

import os

import verifylib


def verify(io):
    failures = []
    live = io.out / "live"
    target = live / "app.conf"
    if not target.is_file():
        return ["missing live/app.conf"]

    expected = (io.inp / "update.valid").read_text(encoding="utf-8")
    if target.read_text(encoding="utf-8") != expected:
        failures.append("live/app.conf does not hold the valid update")

    leftovers = sorted(entry for entry in os.listdir(live) if entry != "app.conf")
    if leftovers:
        failures.append(f"unexpected files left in live/: {leftovers}")

    reject = io.out / "reject.log"
    if not reject.is_file():
        failures.append("missing reject.log")
    elif reject.read_text(encoding="utf-8").strip() != "rejected update.invalid:2":
        failures.append(f"reject.log: expected one rejection of update.invalid:2, got {reject.read_text()!r}")

    failures += verifylib.json_eq(
        io.out / "summary.json", {"applied": True, "rejected": True, "mode": "640"}
    )
    return failures
