"""Grader for 146-context-compression."""

import json

import verifylib

EXPECTED = [
    {"idx": 1, "role": "user", "content": "Please inspect the error in src/main.py and fix it."},
    {"idx": 2, "role": "tool", "tool": "read_file", "output": "[READ: 12 lines, 138 chars]"},
    {"idx": 3, "role": "tool", "tool": "read_file", "output": "[READ: 1 lines, 29 chars]"},
    {"idx": 4, "role": "tool", "tool": "edit_file", "output": "[EDIT: ok]"},
    {
        "idx": 5,
        "role": "assistant",
        "content": "Found it on line 42: a missing comma in the print call. Patched it.",
    },
    {
        "idx": 6,
        "role": "tool",
        "tool": "bash",
        "output": "collected 9 items\n.........    [100%]\n\n9 passed in...[truncated]..."
        "arnings; coverage 96% of statements in src/main.py",
    },
    {"idx": 7, "role": "tool", "tool": "bash", "output": "OK"},
    {
        "idx": 8,
        "role": "tool",
        "tool": "grep",
        "output": "src/main.py:42:    print('total: ' total)\nsrc/util.py:17:    print('total: ' + "
        "total)\nsrc/util.py:31...",
    },
    {"idx": 9, "role": "tool", "tool": "edit_file", "output": "[EDIT: failed]"},
    {"idx": 10, "role": "tool", "tool": "read_file", "output": "[READ: 0 lines, 0 chars]"},
    {"idx": 11, "role": "user", "content": ""},
    {"idx": 12, "role": "system", "content": "You are a careful coding agent."},
    {
        "idx": 13,
        "role": "tool",
        "tool": "bash",
        "output": "9 passed in 0.42s; coverage 96% of statements; 1 warning: deprecated "
        "os.path usage in main.py (docs)",
    },
]


def verify(io) -> list[str]:
    path = io.out / "compressed.jsonl"
    if not path.is_file():
        return ["missing compressed.jsonl"]

    raw = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    failures: list[str] = []
    if len(raw) != len(EXPECTED):
        failures.append(f"compressed.jsonl: expected {len(EXPECTED)} lines, got {len(raw)}")

    for index, (line, want) in enumerate(zip(raw, EXPECTED), start=1):
        try:
            got = json.loads(line)
        except json.JSONDecodeError as exc:
            failures.append(f"compressed.jsonl line {index}: not JSON ({exc}): {line!r}")
            continue
        if got != want:
            failures.append(f"compressed.jsonl line {index}: expected {want!r}, got {got!r}")

    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "total_messages": 13,
            "tool_messages": 9,
            "original_chars": 775,
            "compressed_chars": 571,
            "saved_chars": 204,
            "compression_ratio": 0.7368,
        },
    )
    return failures
