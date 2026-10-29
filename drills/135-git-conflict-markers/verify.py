"""Grader for 135-git-conflict-markers."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "conflicts.csv",
        [
            "file",
            "start_line",
            "end_line",
            "our_branch",
            "their_branch",
            "our_lines",
            "their_lines",
        ],
        [
            (".github/workflows/ci.yml", 7, 14, "HEAD", "ci/pin-actions", 2, 3),
            ("config/settings.json", 3, 10, "HEAD", "feature/retry-policy", 2, 3),
            ("src/app.py", 8, 14, "HEAD", "feature/paths", 2, 2),
            ("src/app.py", 18, 24, "HEAD", "fix/return", 1, 1),
            ("src/legacy.js", 2, 7, "HEAD", "1a2b3c4d (feat: retry policy)", 1, 2),
            ("src/lib/util.ts", 2, 8, "HEAD", "refactor/slug", 1, 1),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "files_scanned": 11,
            "conflicted_files": 5,
            "total_conflicts": 6,
            "clean_files": 6,
            "max_conflict_lines": 5,
        },
    )
    return failures
