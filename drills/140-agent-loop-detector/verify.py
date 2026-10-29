"""Grader for 140-agent-loop-detector."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "loops.csv",
        ["start_step", "end_step", "pattern_type", "description"],
        [
            (12, 19, "cycle_2", "read_file <-> grep x3"),
            (21, 28, "cycle_2", "write_file <-> write_file x3"),
            (30, 33, "repeat_action", "run_tests repeated 4x"),
            (40, 47, "cycle_3", "read_file -> grep -> edit_file x2"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "total_steps": 28,
            "status": "looping",
            "loop_count": 4,
            "first_loop_step": 12,
        },
    )
    return failures
