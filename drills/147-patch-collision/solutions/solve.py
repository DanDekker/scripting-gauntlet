#!/usr/bin/env python3
"""Detect conflicting file leases between agents and lay them out in batches."""

import json
import os
from pathlib import Path


def load_leases(path):
    """Return (total data rows, deduped valid leases as (file, agent, start, end))."""
    lines = path.read_text(encoding="utf-8").splitlines()
    total = 0
    leases = []
    seen = set()

    for index, line in enumerate(lines):
        if index == 0:
            continue  # header
        if not line.strip():
            continue
        total += 1
        fields = [field.strip() for field in line.split(",")]
        if len(fields) < 4:
            continue
        agent, file, start, end = fields[0], fields[1], fields[2], fields[3]
        if not agent or not file:
            continue
        if not (start.isdigit() and end.isdigit()):
            continue
        start_line, end_line = int(start), int(end)
        if start_line < 1 or end_line < start_line:
            continue
        lease = (file, agent, start_line, end_line)
        if lease in seen:
            continue
        seen.add(lease)
        leases.append(lease)

    leases.sort(key=lambda lease: (lease[0], lease[2], lease[1], lease[3]))
    return total, leases


def collide(left, right):
    if left[0] != right[0] or left[1] == right[1]:
        return False
    return max(left[2], right[2]) <= min(left[3], right[3])


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    total, leases = load_leases(in_dir / "leases.csv")

    pairs = []
    for i, left in enumerate(leases):
        for right in leases[i + 1 :]:
            if not collide(left, right):
                continue
            first, second = (left, right) if left[1] < right[1] else (right, left)
            pairs.append(
                (
                    first[0],
                    first[1],
                    f"{first[2]}-{first[3]}",
                    second[1],
                    f"{second[2]}-{second[3]}",
                )
            )
    pairs = sorted(set(pairs), key=lambda row: (row[0], row[1], row[3]))

    batches = []
    for lease in leases:
        for batch in batches:
            if not any(collide(lease, other) for other in batch):
                batch.append(lease)
                break
        else:
            batches.append([lease])

    lines = ["file,agent_1,range_1,agent_2,range_2"]
    for row in pairs:
        lines.append(",".join(row))
    (out_dir / "collisions.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    scheduled = []
    for number, batch in enumerate(batches, start=1):
        for lease in batch:
            scheduled.append((number, lease[1], lease[0], f"{lease[2]}-{lease[3]}"))
    scheduled.sort(key=lambda row: (row[0], row[2], row[1]))

    lines = ["batch,agent_id,file,range"]
    for row in scheduled:
        lines.append(f"{row[0]},{row[1]},{row[2]},{row[3]}")
    (out_dir / "schedule.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "total_leases": total,
        "valid_leases": len(leases),
        "collision_pairs": len(pairs),
        "total_batches": len(batches),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
