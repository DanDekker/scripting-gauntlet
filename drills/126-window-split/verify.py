"""Grader for 126-window-split."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "windows.csv",
        ["index", "chars", "text"],
        [
            (
                1,
                199,
                "# Release notes: ledger service\\nThe ledger service now batches writes: each batch is flushed at most once per\\nsecond, a failed flush is retried three times, and the retry counter is reset\\nevery hour.",
            ),
            (
                2,
                156,
                "Config lives in /etc/ledger/config.yaml. Restart the process after editing it;\\nthe watcher only reloads the file every five minutes, which surprises people.",
            ),
            (
                3,
                182,
                "e file every five minutes, which surprises people.\\n\\nThe importer writes to C:\\\\tmp\\\\ledger\\\\import on Windows and to /tmp/ledger/import\\neverywhere else. Both paths are cleaned on start.",
            ),
            (
                4,
                200,
                "Operators keep asking why the retry queue grows during a backfill. The queue is\\nbounded at 10000 entries, and a backfill can outrun the writer for minutes at a\\ntime, so the queue fills, the oldest ent",
            ),
            (
                5,
                200,
                'ries are dropped, and the log fills with\\nwarnings nobody reads until the next incident review. Ask "how long" first, then\\nlook at queue_depth, then at flush_errors, in that order: the metric that move',
            ),
            (6, 41, "s\\nfirst is not the metric that pages you."),
            (
                7,
                100,
                "s\\nfirst is not the metric that pages you.\\n\\nAsk #ledger-support before you change the retry settings.",
            ),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "paragraphs": 5,
            "windows": 7,
            "chars": 1078,
            "max_window": 200,
            "overlap": 50,
        },
    )
    # Every window must respect the budget, and the total must match the summary.
    if (io.out / "windows.csv").is_file():
        _, rows = verifylib.read_csv(io.out / "windows.csv")
        total = 0
        for row in rows:
            if len(row) != 3:
                failures.append(f"windows.csv: expected 3 fields, got {row!r}")
                continue
            try:
                chars = int(row[1])
            except ValueError:
                failures.append(f"windows.csv: chars is not an integer: {row[1]!r}")
                continue
            if chars > 200:
                failures.append(f"windows.csv: window {row[0]} is {chars} chars, over the 200 budget")
            total += chars
        if rows and total != 1078:
            failures.append(f"windows.csv: chars add up to {total}, expected 1078")
    return failures
