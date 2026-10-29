"""Grader for 085-batch-install."""

import verifylib


def verify(io):
    failures = []
    target = io.out / "target"
    expected = {
        "a.conf": "listen=9090\n",
        "b.conf": "timeout=45\n",
        "c.conf": "workers=4\n",
        "d.conf": "retries=3\n",
    }
    if not target.is_dir():
        return ["missing out/target"]
    names = sorted(entry.name for entry in target.iterdir())
    if names != sorted(expected):
        failures.append(f"target files: expected {sorted(expected)}, got {names}")
    for name, content in expected.items():
        path = target / name
        if not path.is_file():
            continue
        if path.read_text(encoding="utf-8") != content:
            failures.append(f"{name}: expected {content!r}, got {path.read_text()!r}")

    reject = io.out / "reject.log"
    if not reject.is_file():
        failures.append("missing reject.log")
    elif reject.read_text(encoding="utf-8").strip() != "rejected batch-b/e.conf:1":
        failures.append(f"reject.log: got {reject.read_text()!r}")

    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"applied_files": 3, "kept_files": 1, "total_files": 4, "rejected_batches": 1},
    )
    return failures
