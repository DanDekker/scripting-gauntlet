"""Grader for 059-safe-renames."""

import verifylib

EXPECTED = {
    "alpha.txt": "BETA\n",
    "beta.txt": "ALPHA\n",
    "archive report.txt": "REPORT\n",
    "scratch 2026.txt": "SCRATCH\n",
    "keep.txt": "KEEP\n",
}
MOVES = [
    ("-scratch.txt", "scratch 2026.txt"),
    ("Q4 report (final).txt", "archive report.txt"),
    ("alpha.txt", "beta.txt"),
    ("beta.txt", "alpha.txt"),
]


def verify(io):
    failures = verifylib.table(io.out / "moves.csv", ["from", "to"], MOVES)
    failures += verifylib.json_eq(
        io.out / "summary.json", {"moved": 4, "untouched": 1}
    )
    tree = io.out / "tree"
    if not tree.is_dir():
        return failures + ["missing out/tree/"]
    found = {p.name for p in tree.iterdir()}
    if found != EXPECTED.keys():
        failures.append(f"out/tree/: expected {sorted(EXPECTED)}, got {sorted(found)}")
    for name, content in EXPECTED.items():
        path = tree / name
        if not path.is_file():
            failures.append(f"out/tree/{name}: expected a regular file")
        elif path.read_text(encoding="utf-8") != content:
            failures.append(f"out/tree/{name}: content changed")
    return failures
