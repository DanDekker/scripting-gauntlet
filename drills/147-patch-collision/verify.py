"""Grader for 147-patch-collision."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "collisions.csv",
        ["file", "agent_1", "range_1", "agent_2", "range_2"],
        [
            ("lib/db.py", "agent-h", "1-100", "agent-i", "100-120"),
            ("src/app.py", "agent-a", "10-25", "agent-b", "20-35"),
            ("src/app.py", "agent-b", "20-35", "agent-f", "30-40"),
            ("src/app.py", "agent-c", "40-50", "agent-f", "30-40"),
            ("src/utils.py", "agent-d", "5-15", "agent-e", "12-20"),
        ],
    )
    failures += verifylib.table(
        io.out / "schedule.csv",
        ["batch", "agent_id", "file", "range"],
        [
            (1, "agent-h", "lib/db.py", "1-100"),
            (1, "agent-a", "src/app.py", "10-25"),
            (1, "agent-f", "src/app.py", "30-40"),
            (1, "agent-d", "src/utils.py", "5-15"),
            (2, "agent-i", "lib/db.py", "100-120"),
            (2, "agent-b", "src/app.py", "20-35"),
            (2, "agent-c", "src/app.py", "40-50"),
            (2, "agent-e", "src/utils.py", "12-20"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "total_leases": 13,
            "valid_leases": 8,
            "collision_pairs": 5,
            "total_batches": 2,
        },
    )
    return failures
