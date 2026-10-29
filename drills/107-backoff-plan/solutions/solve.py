#!/usr/bin/env python3
"""Retry schedule: classify every status first, then plan the retries that earn them."""

import json
import os
from pathlib import Path


def classify(status: int) -> str:
    if 200 <= status <= 299:
        return "success"
    if status == 429:
        return "rate_limited"
    if 500 <= status <= 599:
        return "server_error"
    return "client_error"


def main() -> None:
    inp = Path(os.environ["IN"])
    out = Path(os.environ["OUT"])
    out.mkdir(parents=True, exist_ok=True)

    log = inp / "requests.log"
    config_path = inp / "config.json"
    for path in (log, config_path):
        if not path.is_file():
            raise SystemExit(f"missing input: {path}")

    config = json.loads(config_path.read_text(encoding="utf-8"))
    base = int(config["base_seconds"])
    max_attempts = int(config["max_attempts"])

    rows: list[tuple[str, int, int]] = []
    requests = success = retryable = client_errors = exhausted = 0

    for raw in log.read_text(encoding="utf-8").splitlines():
        fields = raw.split()
        if len(fields) < 4:
            continue
        requests += 1
        method, path, status_text = fields[1], fields[2], fields[3]
        try:
            status = int(status_text)
        except ValueError:
            client_errors += 1
            continue

        kind = classify(status)
        if kind == "success":
            success += 1
            continue
        if kind == "client_error":
            client_errors += 1
            continue

        retryable += 1
        label = f"{method} {path} {status_text}"
        retries = max(0, max_attempts - 1)
        for attempt in range(1, retries + 1):
            rows.append((label, attempt, base * 2 ** (attempt - 1)))
        if 1 + retries >= max_attempts:
            exhausted += 1

    lines = ["request,attempt,wait_seconds"]
    lines += [f"{label},{attempt},{wait}" for label, attempt, wait in rows]
    (out / "schedule.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "requests": requests,
        "success": success,
        "retryable": retryable,
        "client_errors": client_errors,
        "retries": len(rows),
        "exhausted": exhausted,
        "total_wait": sum(wait for _, _, wait in rows),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
