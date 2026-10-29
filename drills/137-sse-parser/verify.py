"""Grader for 137-sse-parser."""

import verifylib

MESSAGE = "Thé system timeout First line.\nSecond line."


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "chunks.csv",
        ["chunk_index", "delta_len", "role"],
        [
            (1, 0, "assistant"),
            (2, 3, ""),
            (3, 7, ""),
            (4, 8, ""),
            (5, 25, ""),
            (6, 0, ""),
            (7, 0, ""),
        ],
    )
    failures += verifylib.lines(io.out / "message.txt", MESSAGE.splitlines())
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "total_events": 12,
            "comment_lines": 2,
            "valid_chunks": 7,
            "malformed_chunks": 1,
            "total_chars": len(MESSAGE),
            "completed_done": True,
            "prompt_tokens": 31,
            "completion_tokens": 8,
        },
    )

    message = io.out / "message.txt"
    if message.is_file():
        text = message.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            failures.append("message.txt: a non-empty message must end with a newline")
        if text != MESSAGE + "\n":
            failures.append("message.txt: must be the message plus one trailing newline")
    return failures
