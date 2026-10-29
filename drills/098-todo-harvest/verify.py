"""Grader for 098-todo-harvest."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "todos.csv",
        ["file", "line", "marker", "owner", "text"],
        [
            ("app/api.js", 1, "TODO", "bob", "paginate the results"),
            ("app/api.js", 2, "TODO", "", "check the timeout"),
            ("app/main.py", 5, "TODO", "alice", "validate the path before opening"),
            ("app/util.py", 2, "TODO", "", "untangle the retry loop"),
            (
                "docs/release-notes.md",
                3,
                "TODO",
                "pp",
                "rewrite the changelog # TODO(bob): then tag the build",
            ),
            ("lib/vendor/legacy.js", 2, "TODO", "pp", "drop the legacy shim"),
            ("lib/workers/README.txt", 5, "TODO", "ops", "rotate the worker token after the deploy"),
            (
                "lib/workers/queue.py",
                5,
                "TODO",
                "pp",
                "bound the queue; it grows without limit under load",
            ),
            ("scripts/deploy.sh", 4, "TODO", "qa", "gate this behind a dry-run flag; FIXME when the flag lands"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "files_scanned": 9,
            "todos": 9,
            "owners": 5,
            "orphans": 2,
            "by_marker": {"TODO": 9},
        },
    )
    return failures
