#!/usr/bin/env python3
"""Replay recorded attempts through the provider fallback chain."""

import csv
import json
import os
from pathlib import Path


def load_tasks(path):
    tasks = []
    seen = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict) or "task_id" not in record:
            continue
        task_id = str(record["task_id"])
        if task_id in seen:
            continue
        seen.add(task_id)
        tasks.append(task_id)
    return sorted(tasks)


def load_tiers(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    tiers = []
    for record in data:
        tiers.append(
            (
                int(record["tier"]),
                int(record["timeout_ms"]),
                int(record.get("max_retries") or 0),
            )
        )
    tiers.sort(key=lambda row: row[0])
    return tiers


def load_attempts(path):
    attempts = {}
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        next(reader, None)
        for raw in reader:
            cells = [cell.strip() for cell in raw]
            if len(cells) != 5 or not any(cells):
                continue
            task_id, tier_raw, attempt_raw, status_raw, latency_raw = cells
            try:
                key = (task_id, int(tier_raw), int(attempt_raw))
                status = int(status_raw)
                latency = int(latency_raw)
            except ValueError:
                continue
            if not task_id:
                continue
            attempts[key] = (status, latency)
    return attempts


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    tasks = load_tasks(in_dir / "tasks.jsonl")
    tiers = load_tiers(in_dir / "providers.json")
    attempts = load_attempts(in_dir / "attempts.csv")

    rows = []
    success_count = 0
    failed_count = 0
    fallback_invoked = 0
    total_latency = 0

    for task_id in tasks:
        outcome = "failed"
        resolved = ""
        count = 0
        latency_sum = 0
        resolved_tier = None

        for tier, timeout_ms, max_retries in tiers:
            for attempt in range(1, 2 + max_retries):
                recorded = attempts.get((task_id, tier, attempt))
                if recorded is None:
                    break
                status, latency = recorded
                count += 1
                latency_sum += latency
                if status == 200 and latency <= timeout_ms:
                    outcome = "success"
                    resolved = str(tier)
                    resolved_tier = tier
                    break
            if resolved_tier is not None:
                break

        if outcome == "success":
            success_count += 1
            if resolved_tier > 1:
                fallback_invoked += 1
        else:
            failed_count += 1
        total_latency += latency_sum
        rows.append((task_id, outcome, resolved, count, latency_sum))

    with (out_dir / "resolutions.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(
            ["task_id", "outcome", "resolved_tier", "attempts_count", "total_latency_ms"]
        )
        for row in rows:
            writer.writerow(row)

    summary = {
        "total_tasks": len(rows),
        "success_count": success_count,
        "failed_count": failed_count,
        "fallback_invoked": fallback_invoked,
        "total_latency_ms": total_latency,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
