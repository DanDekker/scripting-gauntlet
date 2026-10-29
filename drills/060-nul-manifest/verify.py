"""Grader for 060-nul-manifest."""

import hashlib

import verifylib

CONTENTS = {
    "-dash.txt": "dash\n",
    "docs/quarterly report (final).txt": "Q4\n",
    "docs/line\nbreak.txt": "line\n",
    "docs/tab\tname.txt": "tab\n",
    "empty.txt": "",
    "notes/.hidden": "secret\n",
}


def verify(io):
    expected = [
        {
            "path": path,
            "bytes": len(content.encode()),
            "sha256": hashlib.sha256(content.encode()).hexdigest(),
        }
        for path, content in sorted(CONTENTS.items())
    ]
    failures = verifylib.json_eq(io.out / "manifest.json", expected)
    failures += verifylib.json_eq(
        io.out / "summary.json", {"files": 6, "bytes": 24, "empty": 1}
    )
    return failures
